Changes to the HUF Package for MODFLOW-2005 version 1.5


A bug was fixed to allow proper handling of SY parameters.  Previously,
contributions to the coefficient matrix from multiple SY parameters/clusters
were not summed; only the last cluster processed by the storage conversion
routine made a contribution. This resulted in erroneous handling of unconfined
storage when more than one SY parameter or cluster was applied at a given cell.  

Changes were made to the HUF Package (Anderman and Hill, 2000) to calculate
the vertical hydraulic conductivity and specific yield for all cells in the
uppermost active finite difference cells at the beginning of a simulation. 
These values are required for simulations that include both the HUF Package
and the UZF Package (Niswonger and others, 2006). These changes to the HUF
package do not affect any other calculations in the Package and should not
affect HUF Package results.


Changes to the HUF Package for MODFLOW-2005 version 1.0.

The logic that controls writing of interpolated heads and flows by HUF
was changed from that in the MODFLOW-2000 version of HUF.  The new logic
differs from the original logic as follows:

For interpolated heads:
  o  The "SAVE HEADS" option (or the equivalent numeric controls) must
     be specified for interpolated heads to be written.

  o  If IOHUFHEADS is not 0, its sign determines whether interpolated
     heads are printed to the listing file or saved on unit IOHUFHEADS. 
     (Originally, they were written to both if IOHUFHEADS>0, and there
     was no IOHUFHEADS<0 option.)

For interpolated cell-by-cell flows:
  o  The "SAVE BUDGET" option (or the equivalent numeric control) must be
     specified for interpolated cell-by-cell flows to be written.


IOHUFHEADS - is a flag and a unit number.
       <0 Interpolated heads will be computed and printed to the listing
          file for each hydrogeologic unit, using the format defined in the
          output-control file when "SAVE HEADS" is specified or
          (equivalently) when nonzero values are specified for IHDDFL and
          for Hdsv in at least one layer.  (If no print format has been
          defined, printing will be in 10G11.4 format.)

       0  Interpolated heads will not be computed or written anywhere.

       >0 Interpolated heads will be computed and saved to unit IOHUFHEADS
          for each hydrogeologic unit, using the format defined in the
          output-control file when "SAVE HEADS" is specified or
          (equivalently) when nonzero values are specified for IHDDFL and
          for Hdsv in at least one layer.  (If no print format has been
          defined, saving will be in binary format.)

IOHUFFLOWS - is a flag and a unit number.
       0  Interpolated cell-by-cell flows will not be computed or written
           anywhere.

       >0 Interpolated cell-by-cell flows will be computed and saved to
           unit IOHUFFLOWS for each hydrogeologic unit, in binary format,
           when "SAVE BUDGET" or (equivalently) a nonzero value for ICBCFL
           is specified.




References

Anderman, E.R., and Hill, M.C., 2000, MODFLOW-2000, the U.S. Geological
Survey modular ground-water model—Documentation of the Hydrogeologic-Unit
Flow (HUF) Package: U.S. Geological Survey Open-File Report 2000-342, 89 p.

Niswonger, R.G., Prudic, D.E., and Regan, R.S., 2006, Documentation of the
Unsaturated-Zone Flow (UZF1) Package for modeling unsaturated flow between
the land surface and the water table with MODFLOW-2005: U.S. Geological
Survey Techniques and Methods Book 6, Chapter A19, 62 p.

