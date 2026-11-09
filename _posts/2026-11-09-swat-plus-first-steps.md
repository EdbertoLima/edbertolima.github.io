---
title: "First steps with SWAT+: what every beginner needs to know"
excerpt: "A practical guide to getting started with watershed modelling in SWAT+, based on the short course I taught at SNCT 2026, IFBA Vitória da Conquista, Brazil."
tags:
  - SWAT+
  - hydrological modelling
  - QGIS
toc: true
toc_sticky: true
---

*Este post também está disponível [em português](/primeiros-passos-swat-plus/).*

In October 2026 I taught the short course **"Introduction to SWAT+ for beginners"** at the
National Science and Technology Week (SNCT 2026) of IFBA, Vitória da Conquista campus, Brazil:
8 hours over two days, for students and professionals who had never used SWAT. This post
collects the points that helped participants most. It does not replace the documentation, but it
shows the path and the most common stumbling blocks.

<figure>
  <img src="/assets/images/posts/swat-course-snct-2026.jpg" alt="Participants of the SWAT+ short course in the IFBA GIS lab, with the instructor on the projection screen">
  <figcaption>Participants of the MC07 short course at SNCT 2026, IFBA Vitória da Conquista. I taught the course remotely from Austria (on screen).</figcaption>
</figure>

## What SWAT+ is

**SWAT+** (*Soil and Water Assessment Tool Plus*) is a watershed model that is **continuous in
time** (daily time step), **semi-distributed** and **physically based**: its parameters come from
soil, land use and topography, and have physical meaning. It estimates streamflow, the water
balance, sediments, nutrients and the effect of management, land-use and climate scenarios.

SWAT+ is a complete restructuring of SWAT 2012, developed by USDA-ARS and Texas A&M University.
The process equations are the same; the organisation is different:

| Aspect | SWAT 2012 | SWAT+ |
| --- | --- | --- |
| GIS interface | ArcSWAT (ArcGIS, commercial) or QSWAT | QSWAT+ (QGIS, free) |
| Database | Microsoft Access | SQLite |
| Connections between units | `fig.fig` file, rigid | Connect files (`.con`), flexible |
| Spatial hierarchy | Watershed, subbasins, HRUs | Watershed, subbasins, landscape units (LSUs), HRUs and water areas |
| Management | By date or heat units | Also by decision tables |
| Calibration | Edits the input files | `calibration.cal` overrides values without changing the originals |

The unit of calculation is still the **HRU** (*hydrologic response unit*): a unique combination
of landscape unit, land use, soil and slope class. An HRU has no continuous location; it is the
sum of all cells with the same combination.

## Three programs, one model

The first source of confusion is that SWAT+ is in practice a set of three programs:

| Component | What it does |
| --- | --- |
| **QSWAT+** (QGIS plugin) | Builds the spatial part: delineates the watershed, creates LSUs and HRUs, visualises results. **It is not the model.** |
| **SWAT+ Editor** | Imports climate data, sets the period, options and outputs, writes the text files and runs the model |
| **SWAT+** (executable) | The model itself: reads the text files in `TxtInOut` and writes the outputs |

Everything comes with the [official SWAT+ installer](https://swatplus.gitbook.io/docs/installation).
Use the **64-bit QGIS LTR**, the version tested by the developers, and tick the optional global
weather generator download during installation.

## The data you need

A basic model needs five datasets, **all in the same metric projection**:

| Data | Purpose | Example sources (Brazil) |
| --- | --- | --- |
| Digital elevation model | Drainage, subbasins, slope | SRTM 30 m, Copernicus GLO-30, ANADEM (ANA), TOPODATA (INPE) |
| Land use and land cover | Plants, Curve Number and management for each HRU | [MapBiomas](https://brasil.mapbiomas.org/) (annual collections, 30 m) |
| Soils | Layers, texture, available water, conductivity | IBGE and Embrapa maps; SoilGrids to fill in properties |
| Daily climate | Precipitation, temperature, radiation, humidity, wind | INMET (BDMEP), ANA Hidroweb, BR-DWGD grid, CHIRPS, ERA5 |
| Observed streamflow | Evaluation, calibration and validation | ANA Hidroweb / SNIRH |

In practice, the hardest dataset is almost always the **soil property table** (*usersoil*):
depth, bulk density, available water and conductivity for every layer.

Two rules prevent most errors:

- QSWAT+ assumes **all cells have the same area**. A DEM in degrees (latitude/longitude) must be
  reprojected first, to the UTM zone of the watershed or to an equal-area projection for large
  basins.
- Folder and file names **without spaces, accents or special characters**.

## Checklist before opening QSWAT+

Half an hour of checking here saves hours later:

- [ ] DEM, land use and soil maps share the same projected coordinate system
- [ ] The DEM's vertical unit is metres
- [ ] Land use and soil cover the whole watershed, with no *NoData* holes
- [ ] Every land-use raster value exists in the land-use lookup table
- [ ] Every soil raster value exists in the soil lookup table, and every soil exists in *usersoil*
- [ ] The outlet lies on (or within 300 m of) the generated drainage network
- [ ] The climate record covers the simulation period plus the warm-up years
- [ ] Station coordinates are in decimal degrees, negative for South and West

## The workflow in six steps

1. **Create the project** in QSWAT+ (SWAT+ button in QGIS, *New Project*).
2. **Delineate the watershed:** load the DEM, set the channel and stream thresholds (smaller
   thresholds give more subbasins and a slower model), and add the outlet.
3. **Create landscape units:** separate floodplain and upslope areas (the *DEM inversion* method
   with default values is a good start).
4. **Generate HRUs:** land-use and soil maps with their lookup tables, slope classes, and a filter
   to drop small combinations (for example 10% for land use, soil and slope).
5. **Configure in the SWAT+ Editor:** import the weather generator and observed climate, set the
   period and the **warm-up years** (1 to 3), and choose the outputs.
6. **Run and check:** a successful run ends with *Execution successfully completed* in
   `simulation.out`. Then use **SWAT+ Check**, which flags suspicious values (but does not tell you
   the model is wrong).

To learn, start with the Robit example dataset (Ethiopia) that comes with the installer: it lets
you separate software problems from problems in your own data.

## Common errors and where to look

| Symptom | Likely cause |
| --- | --- |
| The outlet does not snap to the drainage (*0 snapped*) | Point too far from the network, or stream threshold too large |
| Error reading land use or soil | Raster value missing from the lookup table, or different projections |
| No rain anywhere | Station coordinates outside the watershed (sign of latitude/longitude) |
| Almost all flow is surface runoff | Curve Numbers too high, or wrong hydrologic soil group |
| Crops do not grow | No management assigned, or planting outside the period |
| The model stops right away | Climate does not cover the period, or a referenced file is missing |

## Before calibrating: does the water balance make sense?

A model with a beautiful hydrograph and an absurd water balance is right for the wrong reasons.
Before comparing with observed streamflow, open `basin_wb_aa.txt` (average annual watershed
balance) and check:

- **Closure:** precipitation ≈ evapotranspiration + surface runoff + lateral flow + percolation +
  change in storage.
- **ET/P** consistent with the regional climate (ET higher than precipitation is a red flag).
- **Flow partitioning:** in a perennial watershed with an aquifer, nearly all flow as surface
  runoff points to Curve Numbers that are too high.
- **Vegetation:** near-zero biomass in agricultural HRUs points to a management problem.

Only then comes calibration: first **soft calibration** (matching the water-balance fractions to
regional values), then **hard calibration** against observed streamflow, and finally
**validation** on an independent period. As a reference for monthly streamflow,
[Moriasi et al. (2007)](https://doi.org/10.13031/2013.23153) consider NSE > 0.50, |PBIAS| < 25% and
RSR ≤ 0.70 satisfactory.

## Keep learning

- The [official SWAT+ page](https://swat.tamu.edu/software/plus/) and the
  [documentation](https://swatplus.gitbook.io/docs/installation), with a reference for every
  input and output file.
- The QSWAT+ tutorial and the SWAT+ Editor manual, installed with the software.
- The SWAT+ user group and the annual SWAT conferences.
- After your first model: decision tables for management, automatic calibration, and land-use
  and climate scenarios.

## References

- Arnold, J. G., Čerkasova, N., White, M., et al. *Soil and Water Assessment Tool Plus (SWAT+)*.
  Zenodo. [doi:10.5281/zenodo.14983533](https://doi.org/10.5281/zenodo.14983533)
- Moriasi, D. N., Arnold, J. G., Van Liew, M. W., Bingner, R. L., Harmel, R. D., & Veith, T. L.
  (2007). Model evaluation guidelines for systematic quantification of accuracy in watershed
  simulations. *Transactions of the ASABE, 50*(3), 885-900.
  [doi:10.13031/2013.23153](https://doi.org/10.13031/2013.23153)
- Neitsch, S. L., Arnold, J. G., Kiniry, J. R., & Williams, J. R. (2011). *Soil and Water
  Assessment Tool Theoretical Documentation, Version 2009*. Texas A&M University.
