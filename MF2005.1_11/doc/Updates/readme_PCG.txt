Changes to the PCG7 Package for MODFLOW-2005 version 1.9:

Added the IHCOFADD option. When an active cell is surrounded by dry cells,
the cell normally converts to dry.  The new option causes the cell to
convert to dry only if storage and head-dependent boundary flow are also 0.
IHCOFADD is a 4th integer input item read on the first input line.  A
non-zero value activates the option.  An unspecified or 0 value turns the
option off.

Changes to the PCG7 Package for MODFLOW-2005 version 1.5:

The option was added to the PCG7 Package to have separate damping factors
(input variable DAMP, Harbaugh, 2005, p 8-53) for steady-state and transient
stress periods within a single simulation. In some cases, a lower damping
factor is needed for steady state stress periods than for transient stress
periods.  The single variable DAMP is replaced by two variables, DAMPPCG and
DAMPPCGT.  DAMPPCG is required, and DAMPPCGT is optional. The option of
having two damping factors is activated by specifying a negative value
for DAMPPCG, indicating that a second damping factor used for transient
stress periods will be read. The value of DAMPPCG is made into a positive
value before being used, and this values is used for steady-state stress
periods. The two damping factors are included in Item 2 of the PCG7 input
file.  The complete input instructions for PCG follow.


                REVISED PCG INPUT INSTRUCTIONS

Input to the Preconditioned Conjugate-Gradient (PCG) Package is read from
the file that is type "PCG" in the Name File. All numeric variables are free
format if the option "FREE" is specified in the Basic Package input file;
otherwise, all the variables have 10-character fields.

FOR EACH SIMULATION
  0.   [#Text]
     Item 0 is optional -- "#" must be in column 1.  Item 0 can be repeated
     multiple times.

  1. MXITER    ITER1    NPCOND   [IHCOFADD]

  2. HCLOSE    RCLOSE   RELAX   NBPOL   IPRPCG  MUTPCG   DAMPPCG [DAMPPCGT]

   Explanation of Variables Read by the PCG Package

Text-- is a character variable (199 characters) that starts in column 2.
Any characters can be included in Text. The "#" character must be in
column 1. Except for the Name File, lines beginning with # are restricted
to these first lines of the file. Text is written to the Listing File.

MXITER-- is the maximum number of outer iterations. For a linear problem
MXITER should be 1, unless more than 50 inner iterations are required, when
MXITER could be as large as 10. A larger number (generally less than 100)
is required for a nonlinear problem.

ITER1-- is the number of inner iterations. For nonlinear problems, ITER1
usually ranges from 10 to 30; a value of 30 will be sufficient for most
linear problems.

NPCOND-- is the flag used to select the matrix conditioning method:
  1-- is for Modified Incomplete Cholesky (for use on scalar computers)
  2-- is for Polynomial (for use on vector computers or to conserve computer
      memory)

IHCOFADD-- is a flag that determines what happens to an active cell that is
surrounded by dry cells:
  0-- cell converts to dry regardless of HCOF value. This is the default,
      which is the way PCG2 worked prior to the addition of this option.
  Not 0-- cell converts to dry only if HCOF is 0 (no head-dependent stresses
      or storage terms).

HCLOSE-- is the head change criterion for convergence, in units of length.
When the maximum absolute value of head change from all nodes during an
iteration is less than or equal to HCLOSE, and the criterion for RCLOSE
is also satisfied, iteration stops.

RCLOSE-- is the residual criterion for convergence, in units of cubic
length per time.  The units for length and time are the same as established
for all model data.  (See LENUNI and ITMUNI input variables in the
Discretizations File.)  When the maximum absolute value of the residual at
all nodes during an iteration is less than or equal to RCLOSE, and the
criterion for HCLOSE is also satisfied, iteration stops.

  For nonlinear problems, convergence is achieved when the convergence
  criteria are satisfied for the first inner iteration.

RELAX-- is the relaxation parameter used with NPCOND = 1. Usually,
RELAX = 1.0, but for some problems a value of 0.99, 0.98, or 0.97 will
reduce the number of iterations required for convergence. RELAX is not used
if NPCOND is not 1.

NBPOL-- is used when NPCOND=2 to indicate whether the estimate of the upper
bound on the maximum eigenvalue is 2.0, or whether the estimate will be
calculated. NBPOL=2 is used to specify the value is 2.0; for any other
value of NBPOL, the estimate is calculated. Convergence is generally
insensitive to this upper bound. NBPOL is not used if NBPOL is not 2.

IPRPCG-- is the printout interval for PCG. IPRPCG, if equal to zero, is
changed to 999. The maximum head change (positive or negative) and
residual change are printed for each iteration of a time step whenever the
time step is an even multiple of IPRPCG. This printout also occurs at the
end of each stress period regardless of the value of IPRPCG.

MUTPCG-- is a flag that controls printing of convergence information from
the solver:
  0-- is for printing tables of maximum head change and residual each iteration
  1-- is for printing only the total number of iterations
  2-- is for no printing
  3-- is for printing only if convergence fails

DAMPPCG-- is the damping factor. It is typically set equal to one, which
indicates no damping.  A value less than 1 and greater than 0 causes damping.
 >0 -- applies to both steady-state and transient stress periods.
 <0 -- applies only to steady-sate stress periods.  The absolute value is
       used as the damping factor.
 
DAMPPCGT-- is the damping factor for transient stress periods. DAMPPCGT
is enclosed in brackets indicating that it is an optional variable that
only is read when DAMPPCG is specified as a negative value.  If DAMPPCGT is
not read, then the single damping factor, DAMPPCG, is used for both
transient and steady-state stress periods.


References

Harbaugh, A.W., 2005, MODFLOW-2005, the U.S. Geological Survey modular
ground-water model-the Ground-Water Flow Process: U.S. Geological Survey
Techniques and Methods 6-A16, variously paginated.

