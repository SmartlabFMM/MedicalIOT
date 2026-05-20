from pathlib import Path
import xml.etree.ElementTree as ET

tmp = Path(r"D:\odoo-19\custom_addons\med_iot_command_center\static\src\xml\dashboard_FIXED_TEST.xml")
xml = tmp.read_text(encoding="utf-8")

ET.parse(tmp)

ph = 'placeholder="Search patient..."'
idx = xml.find(ph)
input_start = xml.rfind("<input", 0, idx)
input_end = xml.find('<i class="fa fa-search"', idx)
input_block = xml[input_start:input_end]

opt = '<option value="">All Status</option>'
opt_idx = xml.find(opt)
select_start = xml.rfind("<select", 0, opt_idx)
select_end = xml.find(opt, select_start) + len(opt)
select_block = xml[select_start:select_end]

print("input t-on-input count:", input_block.count("t-on-input="))
print("select t-on-change count:", select_block.count("t-on-change="))

if input_block.count("t-on-input=") != 1:
    raise SystemExit("BAD INPUT")

if select_block.count("t-on-change=") != 1:
    raise SystemExit("BAD SELECT")

if 't-on-input="(ev) =' in xml:
    raise SystemExit("BAD CORRUPTED INPUT TEXT")

print("FINAL CHECK OK - SAFE TO APPLY")
