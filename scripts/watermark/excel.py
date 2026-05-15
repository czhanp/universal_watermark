from __future__ import annotations

import re
import zipfile
from pathlib import Path
from typing import Optional

from .common import (
    add_override_content_type,
    add_png_content_type,
    create_watermark_layer,
    empty_relationships_root,
    find_font,
    layer_to_png_bytes,
    next_rid,
    qn,
    read_xml_from_zip,
    rels_path_for_part,
    resolve_rel_target,
)
from .constants import A_NS, CT_NS, PKG_REL_NS, R_NS, XDR_NS, XL_NS
from .options import WatermarkOptions


def col_letters_to_index(letters: str) -> int:
    """Excel 列字母转 1-based 列号。A -> 1。"""
    n = 0
    for ch in letters.upper():
        if "A" <= ch <= "Z":
            n = n * 26 + (ord(ch) - ord("A") + 1)
    return max(1, n)


def parse_cell_ref(cell_ref: str) -> tuple[int, int]:
    """解析 A1 / BC23，返回 1-based (col, row)。"""
    m = re.match(r"^([A-Za-z]+)(\d+)$", cell_ref or "")
    if not m:
        return 1, 1
    return col_letters_to_index(m.group(1)), int(m.group(2))


def get_xlsx_sheet_extent(ws_root) -> tuple[int, int]:
    """估算工作表已使用范围，返回 1-based 最大列和最大行。"""
    max_col, max_row = 1, 1
    dim = ws_root.find(qn(XL_NS, "dimension"))
    if dim is not None and dim.get("ref"):
        last = dim.get("ref").split(":")[-1]
        c, r = parse_cell_ref(last)
        max_col, max_row = max(max_col, c), max(max_row, r)

    # dimension 有时不可靠，补充扫描 c/@r
    for cell in ws_root.findall(f".//{qn(XL_NS, 'c')}"):
        c, r = parse_cell_ref(cell.get("r", "A1"))
        max_col, max_row = max(max_col, c), max(max_row, r)
    return max_col, max_row


def insert_worksheet_child_before_extlst(ws_root, child) -> None:
    children = list(ws_root)
    ext_lst = ws_root.find(qn(XL_NS, "extLst"))
    if ext_lst is not None:
        ws_root.insert(children.index(ext_lst), child)
    else:
        ws_root.append(child)


def insert_worksheet_drawing(ws_root, drawing_el) -> None:
    """drawing 元素应尽量位于 picture 背景元素之前。"""
    children = list(ws_root)
    picture = ws_root.find(qn(XL_NS, "picture"))
    if picture is not None:
        ws_root.insert(children.index(picture), drawing_el)
    else:
        insert_worksheet_child_before_extlst(ws_root, drawing_el)


def remove_xlsx_sheet_background(ws_root, rels_root) -> None:
    """删除工作表背景图片节点；主要用于替换旧背景，避免一个 sheet 有多个 picture。"""
    bg_rids = []
    for pic in list(ws_root.findall(qn(XL_NS, "picture"))):
        rid = pic.get(qn(R_NS, "id"))
        if rid:
            bg_rids.append(rid)
        ws_root.remove(pic)
    for rel in list(rels_root.findall(qn(PKG_REL_NS, "Relationship"))):
        if rel.get("Id") in bg_rids:
            rels_root.remove(rel)


def remove_old_xlsx_overlay_watermarks(drawing_root, drawing_rels_root) -> None:
    """删除本脚本之前添加的 Excel 浮层水印，避免重复叠加。"""
    for anchor in list(drawing_root):
        c_nv_pr = anchor.find(f".//{qn(XDR_NS, 'cNvPr')}")
        if c_nv_pr is not None and c_nv_pr.get("name", "").startswith("UniversalExcelWatermark"):
            drawing_root.remove(anchor)
    for rel in list(drawing_rels_root.findall(qn(PKG_REL_NS, "Relationship"))):
        if "universal_excel_watermark" in rel.get("Target", ""):
            drawing_rels_root.remove(rel)


def next_xlsx_drawing_index(existing_names: list[str]) -> int:
    max_idx = 0
    for name in existing_names:
        m = re.fullmatch(r"xl/drawings/drawing(\d+)\.xml", name)
        if m:
            max_idx = max(max_idx, int(m.group(1)))
    return max_idx + 1


def make_empty_xlsx_drawing_root():
    from lxml import etree
    return etree.Element(qn(XDR_NS, "wsDr"), nsmap={"xdr": XDR_NS, "a": A_NS, "r": R_NS})


def find_relationship_target(rels_root, rid: str) -> Optional[str]:
    for rel in rels_root.findall(qn(PKG_REL_NS, "Relationship")):
        if rel.get("Id") == rid:
            return rel.get("Target")
    return None


def make_xlsx_watermark_anchor(rel_id: str, pic_id: int, col_end: int, row_end: int):
    """创建 Excel drawing 中的水印图片 anchor。"""
    from lxml import etree
    anchor = etree.Element(qn(XDR_NS, "twoCellAnchor"), {"editAs": "absolute"})

    frm = etree.SubElement(anchor, qn(XDR_NS, "from"))
    etree.SubElement(frm, qn(XDR_NS, "col")).text = "0"
    etree.SubElement(frm, qn(XDR_NS, "colOff")).text = "0"
    etree.SubElement(frm, qn(XDR_NS, "row")).text = "0"
    etree.SubElement(frm, qn(XDR_NS, "rowOff")).text = "0"

    to = etree.SubElement(anchor, qn(XDR_NS, "to"))
    etree.SubElement(to, qn(XDR_NS, "col")).text = str(max(1, col_end))
    etree.SubElement(to, qn(XDR_NS, "colOff")).text = "0"
    etree.SubElement(to, qn(XDR_NS, "row")).text = str(max(1, row_end))
    etree.SubElement(to, qn(XDR_NS, "rowOff")).text = "0"

    pic = etree.SubElement(anchor, qn(XDR_NS, "pic"))
    nv_pic_pr = etree.SubElement(pic, qn(XDR_NS, "nvPicPr"))
    etree.SubElement(
        nv_pic_pr,
        qn(XDR_NS, "cNvPr"),
        {"id": str(pic_id), "name": f"UniversalExcelWatermark_{pic_id}"},
    )
    c_nv_pic_pr = etree.SubElement(nv_pic_pr, qn(XDR_NS, "cNvPicPr"))
    etree.SubElement(c_nv_pic_pr, qn(A_NS, "picLocks"), {"noChangeAspect": "1"})

    blip_fill = etree.SubElement(pic, qn(XDR_NS, "blipFill"))
    etree.SubElement(blip_fill, qn(A_NS, "blip"), {qn(R_NS, "embed"): rel_id})
    stretch = etree.SubElement(blip_fill, qn(A_NS, "stretch"))
    etree.SubElement(stretch, qn(A_NS, "fillRect"))

    sp_pr = etree.SubElement(pic, qn(XDR_NS, "spPr"))
    prst_geom = etree.SubElement(sp_pr, qn(A_NS, "prstGeom"), {"prst": "rect"})
    etree.SubElement(prst_geom, qn(A_NS, "avLst"))

    etree.SubElement(anchor, qn(XDR_NS, "clientData"))
    return anchor


def watermark_xlsx(input_path: Path, output_path: Path, options: WatermarkOptions) -> Path:
    """
    给 XLSX/XLSM 添加水印。

    Excel 没有真正等同于 Word 的“水印层”。本函数支持三种模式：
    - background：写入 worksheet background picture，位于单元格后方，适合查看和编辑，但通常不参与打印；
    - overlay：插入透明图片浮层，适合随文件显示/打印，但会覆盖在单元格上方；
    - both：同时使用背景和浮层，视觉最明显，但更可能干扰编辑。
    """
    try:
        from lxml import etree
    except ImportError as e:
        raise ImportError("处理 XLSX 需要安装 lxml：pip install lxml") from e

    mode = (options.excel_mode or "background").lower()
    if mode not in {"background", "overlay", "both"}:
        raise ValueError("excel_mode 只能是 background、overlay 或 both")

    font = find_font(options.font_path)
    # Excel 背景图会被平铺，因此生成一个适中的水印图块；浮层图会被拉伸覆盖已用区域。
    layer = create_watermark_layer(1400, 900, options, font)
    png_bytes = layer_to_png_bytes(layer, options.dpi)

    overrides: dict[str, bytes] = {}
    with zipfile.ZipFile(input_path, "r") as zin:
        names = zin.namelist()
        sheet_files = sorted(
            [n for n in names if re.fullmatch(r"xl/worksheets/sheet\d+\.xml", n)],
            key=lambda s: int(re.findall(r"\d+", s)[0]),
        )
        if not sheet_files:
            raise RuntimeError("未找到 Excel 工作表 XML，无法添加水印。")

        ct_root = read_xml_from_zip(zin, "[Content_Types].xml")
        add_png_content_type(ct_root)
        next_drawing_idx = next_xlsx_drawing_index(names)

        for idx, sheet_path in enumerate(sheet_files, start=1):
            ws_root = read_xml_from_zip(zin, sheet_path)
            rels_path = rels_path_for_part(sheet_path)
            rels_root = read_xml_from_zip(zin, rels_path) if rels_path in names else empty_relationships_root()

            if mode in {"background", "both"}:
                # Worksheet background：不遮挡单元格编辑，但通常不会打印。
                remove_xlsx_sheet_background(ws_root, rels_root)
                media_name = f"xl/media/universal_excel_watermark_bg_{idx}.png"
                overrides[media_name] = png_bytes
                rid = next_rid(rels_root)
                etree.SubElement(
                    rels_root,
                    qn(PKG_REL_NS, "Relationship"),
                    {
                        "Id": rid,
                        "Type": "http://schemas.openxmlformats.org/officeDocument/2006/relationships/image",
                        "Target": f"../media/universal_excel_watermark_bg_{idx}.png",
                    },
                )
                pic = etree.Element(qn(XL_NS, "picture"), {qn(R_NS, "id"): rid})
                insert_worksheet_child_before_extlst(ws_root, pic)

            if mode in {"overlay", "both"}:
                # Drawing 浮层：更可能参与打印/导出，但会覆盖在单元格上方，靠透明度降低干扰。
                drawing_el = ws_root.find(qn(XL_NS, "drawing"))
                drawing_path = None
                drawing_rels_path = None
                drawing_root = None
                drawing_rels_root = None

                if drawing_el is not None:
                    drawing_rid = drawing_el.get(qn(R_NS, "id"))
                    target = find_relationship_target(rels_root, drawing_rid) if drawing_rid else None
                    if target:
                        drawing_path = resolve_rel_target(sheet_path, target)

                if drawing_path and drawing_path in names:
                    drawing_root = read_xml_from_zip(zin, drawing_path)
                else:
                    drawing_path = f"xl/drawings/drawing{next_drawing_idx}.xml"
                    next_drawing_idx += 1
                    drawing_root = make_empty_xlsx_drawing_root()
                    drawing_rid = next_rid(rels_root)
                    etree.SubElement(
                        rels_root,
                        qn(PKG_REL_NS, "Relationship"),
                        {
                            "Id": drawing_rid,
                            "Type": "http://schemas.openxmlformats.org/officeDocument/2006/relationships/drawing",
                            "Target": f"../drawings/{Path(drawing_path).name}",
                        },
                    )
                    drawing_el = etree.Element(qn(XL_NS, "drawing"), {qn(R_NS, "id"): drawing_rid})
                    insert_worksheet_drawing(ws_root, drawing_el)
                    add_override_content_type(
                        ct_root,
                        drawing_path,
                        "application/vnd.openxmlformats-officedocument.drawing+xml",
                    )

                drawing_rels_path = rels_path_for_part(drawing_path)
                drawing_rels_root = read_xml_from_zip(zin, drawing_rels_path) if drawing_rels_path in names else empty_relationships_root()
                remove_old_xlsx_overlay_watermarks(drawing_root, drawing_rels_root)

                media_name = f"xl/media/universal_excel_watermark_overlay_{idx}.png"
                overrides[media_name] = png_bytes
                img_rid = next_rid(drawing_rels_root)
                etree.SubElement(
                    drawing_rels_root,
                    qn(PKG_REL_NS, "Relationship"),
                    {
                        "Id": img_rid,
                        "Type": "http://schemas.openxmlformats.org/officeDocument/2006/relationships/image",
                        "Target": f"../media/universal_excel_watermark_overlay_{idx}.png",
                    },
                )

                max_col, max_row = get_xlsx_sheet_extent(ws_root)
                col_end = max(12, min(max_col + 6, 80))
                row_end = max(40, min(max_row + 25, 5000))
                pic_id = 9000 + idx
                anchor = make_xlsx_watermark_anchor(img_rid, pic_id, col_end, row_end)
                drawing_root.insert(0, anchor)

                overrides[drawing_path] = etree.tostring(drawing_root, xml_declaration=True, encoding="UTF-8", standalone=True)
                overrides[drawing_rels_path] = etree.tostring(drawing_rels_root, xml_declaration=True, encoding="UTF-8", standalone=True)

            overrides[sheet_path] = etree.tostring(ws_root, xml_declaration=True, encoding="UTF-8", standalone=True)
            overrides[rels_path] = etree.tostring(rels_root, xml_declaration=True, encoding="UTF-8", standalone=True)

        overrides["[Content_Types].xml"] = etree.tostring(ct_root, xml_declaration=True, encoding="UTF-8", standalone=True)

        with zipfile.ZipFile(output_path, "w", zipfile.ZIP_DEFLATED) as zout:
            for item in zin.infolist():
                name = item.filename
                if name in overrides:
                    zout.writestr(name, overrides.pop(name))
                else:
                    zout.writestr(item, zin.read(name))
            for name, data in overrides.items():
                zout.writestr(name, data)

    return output_path
