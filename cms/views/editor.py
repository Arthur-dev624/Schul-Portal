from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from cms.api import get_page_block_used_in_page, get_layout_regions_of_page

@login_required
def block_verwaltung(request, page_id, version):
    username = request.user.username
    page_blocks_by_region = get_page_block_used_in_page(page_id, version)
    layout_regions = get_layout_regions_of_page(page_id)
    regions_with_blocks = []

    # layout_regions_filled Dictionary mit layout_region.key : Bool
    # True wenn Blöcke in Layoutregion vorhanden, False wenn nicht
    for layout_region in layout_regions:
        blocks = page_blocks_by_region.get(layout_region.key, [])
        regions_with_blocks.append({
            "region": layout_region,
            "blocks": blocks,
        })

    context = {
        "username": username,
        "page_blocks_by_region": page_blocks_by_region,
        "layout_regions": layout_regions,
        "regions_with_blocks": regions_with_blocks,
    }
    return render(request, "blockVerwaltung.html" ,context)

