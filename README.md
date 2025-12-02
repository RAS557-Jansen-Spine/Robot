# Final Project: Foldable Robotics DXF Generator

This project is a tool for designing and generating manufacturing files for foldable robotic mechanisms, specifically focusing on structures like the Jensen Leg. It leverages the `foldable-robotics` library to define laminate structures and `ezdxf` for handling DXF file input and output.

## Features

- **DXF Processing**: Robust reading and writing of DXF files using `dxfv2.py`.
  - Supports `LWPOLYLINE`, `LINE`, and `CIRCLE` entities.
  - Automatically tessellates curved polyline segments (bulges) into discrete vertices.
  - Filters entities by layer and color.
- **Laminate Design**: Uses `foldable-robotics` to define multi-layer laminate devices.
- **Manufacturing Output**: Generates "first pass" and "final cut" DXF files suitable for laser cutting or plotting.

## Project Structure

- `dxf_genmerator.ipynb`: The main Jupyter Notebook that drives the design process, defines the laminate layers, and exports the final DXF files.
- `dxfv2.py`: A utility module for DXF file operations, including geometry extraction and file creation.
- `dxf/`: Directory containing input and output files.
  - `input/`: Source DXF designs (e.g., `jensen-leg.dxf`).
  - `output/`: Generated manufacturing files (e.g., `final_cut.dxf`).
- `pyproject.toml`: Project configuration and dependencies.

## Installation

Ensure you have Python 3.9 or higher installed.

1. **Clone and Install:**
   Run the following commands to clone the specific branch and install dependencies:
   ```bash
   git clone -b cut_file_generator https://github.com/RAS557-Jansen-Spine/Robot.git
   cd Robot
   pip install .
   ```

   *For development (editable install):* `pip install -e .`

   **Key Dependencies:**
   - `foldable-robotics`
   - `ezdxf`
   - `shapely`
   - `matplotlib`
   - `jupyter` (for running the notebook)

## Usage

1. **Prepare Input DXF:**
   Place your base design DXF file in the `dxf/input/` directory. Note that the example input files provided were created using **LibreCAD**. Ensure your geometry is organized into appropriate layers (e.g., "body", "holes") if required by the script.

2. **Run the Generator:**
   Open `dxf_genmerator.ipynb` in Jupyter Notebook or VS Code.
   ```bash
   jupyter notebook dxf_genmerator.ipynb
   ```
   Execute the cells in order. The notebook will:
   - Load the input geometry.
   - Define the laminate structure (hinges, structural layers).
   - Generate the cut files.

3. **Retrieve Outputs:**
   The generated DXF files will be saved in `dxf/output/`.
   - `final_cut.dxf`: The final profile for cutting.
   - `first_pass*.dxf`: Intermediate cuts or etching passes.

## Utility Module (`dxfv2.py`)

You can also use `dxfv2.py` as a standalone library for your own scripts:

```python
from dxfv2 import extract_geometry, write_new_dxf

# Extract geometry from a file
body, holes, circles = extract_geometry("dxf/input/design.dxf", body_layer="body", hole_layer="holes")

# Write a new DXF file
write_new_dxf("dxf/output/new_design.dxf", body_polys=body, slot_polys=holes, circles=circles)
```

