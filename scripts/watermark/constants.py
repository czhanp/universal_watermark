"""全局常量与支持格式集合。"""

W_NS = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
R_NS = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
V_NS = "urn:schemas-microsoft-com:vml"
O_NS = "urn:schemas-microsoft-com:office:office"
PKG_REL_NS = "http://schemas.openxmlformats.org/package/2006/relationships"
CT_NS = "http://schemas.openxmlformats.org/package/2006/content-types"
XL_NS = "http://schemas.openxmlformats.org/spreadsheetml/2006/main"
XDR_NS = "http://schemas.openxmlformats.org/drawingml/2006/spreadsheetDrawing"
A_NS = "http://schemas.openxmlformats.org/drawingml/2006/main"

EMU_PER_INCH = 914400
PT_PER_INCH = 72

SUPPORTED_IMAGES = {"png", "jpg", "jpeg", "webp", "bmp", "tif", "tiff"}
SUPPORTED_WORD_LEGACY = {"doc", "rtf", "odt"}
SUPPORTED_PPT_LEGACY = {"ppt"}
SUPPORTED_EXCEL_OOXML = {"xlsx", "xlsm", "xltx", "xltm"}
SUPPORTED_EXCEL_LEGACY = {"xls", "ods", "csv"}
