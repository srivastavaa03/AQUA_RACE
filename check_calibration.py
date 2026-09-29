import glob
import os
import xml.etree.ElementTree as ET

root = r"D:\S1B_IW_GRDH_1SDV_20200810T013755_20200810T013820_022854_02B625_672D.SAFE"

files = glob.glob(
    root + r"\**\annotation\calibration\calibration-*.xml",
    recursive=True
)

for f in files:
    tree = ET.parse(f)
    root_xml = tree.getroot()

    count = sum(
        1 for e in root_xml.iter()
        if e.tag.split("}")[-1] == "calibrationVector"
    )

    print("\nFILE:", os.path.basename(f))
    print("SIZE:", os.path.getsize(f), "bytes")
    print("CALIBRATION VECTORS:", count)
