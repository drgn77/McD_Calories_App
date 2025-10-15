"""Flask routes for displaying menu, handling cart actions, and summaries."""

from flask import render_template, request, session, redirect, url_for
from .db import list_categories, list_items


def register_routes(app):
    """Register all Flask routes and context processors."""

    @app.get("/")
    def index():
        """Redirect root URL to the main menu page."""
        return redirect(url_for("menu_view"))

    @app.get("/menu")
    def menu_view():
        """Render the product menu with optional filters."""
        category = request.args.get("category")
        q = request.args.get("q", "").strip() or None

        categories = list_categories()
        items = list_items(category=category, q=q)
        cart = session.get("cart", {})

        cat_labels = {
            "beverages": "🥤 Napoje",
            "breakfest": "🍳 Śniadania",
            "classic": "🍔 Klasyki",
            "desserts": "🍨 Desery",
            "fries": "🍟 Frytki",
            "limited": "⭐ Specjały",
            "salads": "🥗 Sałatki",
            "sauces": "🧂 Sosy",
        }

        return render_template(
            "menu.html",
            categories=categories,
            current_category=category,
            q=(q or ""),
            items=items,
            cart=cart,
            cat_labels=cat_labels,
        )

    @app.post("/cart/add")
    def cart_add():
        """Add one unit of a product to the cart."""
        slug = request.form.get("slug")
        qty = int(request.form.get("qty", 1))
        cart = session.get("cart", {})
        if slug:
            cart[slug] = cart.get(slug, 0) + qty
            session["cart"] = cart
        return redirect(request.referrer or url_for("menu_view"))

    @app.post("/cart/remove")
    def cart_remove():
        """Remove one unit of a product from the cart."""
        slug = request.form.get("slug")
        cart = session.get("cart", {})
        if slug in cart:
            if cart[slug] > 1:
                cart[slug] -= 1
            else:
                cart.pop(slug)
            session["cart"] = cart
        return redirect(request.referrer or url_for("menu_view"))

    @app.get("/check")
    def check_view():
        """Render a summary view of the current shopping cart."""
        cart = session.get("cart", {})
        if not cart:
            empty_total = dict(energy_kcal=0, protein_g=0, fat_g=0, carbs_g=0, salt_g=0)
            return render_template("check.html", items=[], cart={}, total=empty_total)

        items = list_items()
        selected = [it for it in items if it["slug"] in cart]

        total = {"energy_kcal": 0, "protein_g": 0, "fat_g": 0, "carbs_g": 0, "salt_g": 0}
        for it in selected:
            qty = cart[it["slug"]]
            total["energy_kcal"] += it["energy_kcal"] * qty
            total["protein_g"] += it["protein_g"] * qty
            total["fat_g"] += it["fat_g"] * qty
            total["carbs_g"] += it["carbs_g"] * qty
            total["salt_g"] += it["salt_g"] * qty

        return render_template("check.html", items=selected, cart=cart, total=total)

    @app.post("/cart/clear")
    def cart_clear():
        """Clear the entire shopping cart."""
        session.pop("cart", None)
        return redirect(url_for("menu_view"))

    @app.context_processor
    def inject_cart_summary():
        """Inject a cart summary object into all templates.

        The injected variable `cart_summary` includes:
            * count (int): total item count
            * kcal (int): total calories
            * protein (float): total protein (g)
        """
        cart = session.get("cart", {})
        summary = {"count": 0, "kcal": 0, "protein": 0.0}
        if cart:
            items = list_items()
            by_slug = {it["slug"]: it for it in items}
            for slug, qty in cart.items():
                it = by_slug.get(slug)
                if not it:
                    continue
                summary["count"] += qty
                summary["kcal"] += int(it["energy_kcal"]) * qty
                summary["protein"] += float(it["protein_g"]) * qty
        return dict(cart_summary=summary)
