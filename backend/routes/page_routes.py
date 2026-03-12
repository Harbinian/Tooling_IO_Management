# -*- coding: utf-8 -*-
"""Template-rendered page routes."""

from flask import Blueprint, render_template

page_bp = Blueprint("page_routes", __name__)


@page_bp.route("/inventory")
def inventory_page():
    return render_template("inventory_list.html")


@page_bp.route("/inventory/create")
def inventory_create_page():
    return render_template("inventory_form.html")


@page_bp.route("/inventory/<order_no>")
def inventory_detail_page(order_no):
    return render_template("inventory_detail.html")


@page_bp.route("/inventory/keeper")
def inventory_keeper_page():
    return render_template("inventory_keeper.html")

