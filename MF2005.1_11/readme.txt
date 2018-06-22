README.TXT


                  MODFLOW-2005 - Version: 1.11.00
         Three-dimensional finite-difference ground-water flow model


NOTE: Any use of trade, product or firm names is for descriptive purposes 
      only and does not imply endorsement by the U.S. Government.

This version of MODFLOW is referred to as MODFLOW-2005 in order to distinguish
it from older versions of the code. This version of MODFLOW-2005 is packaged 
for personal computers using the Microsoft Windows XP or 7 operating
systems.  Executable files for personal computers are provided as well as the
source code.  The source code can be compiled to run on other computers.

IMPORTANT: Users should review the file mf2005.txt for a description of, and
references for, this software. Users should also review the file release.txt,
which describes changes that have been introduced into MODFLOW-2005 with each
official release; these changes may substantially affect users.

Instructions for installation, execution, and testing of MODFLOW-2005 are
provided below.



                            TABLE OF CONTENTS

                         A. DISTRIBUTION FILE
                         B. INSTALLING
                         C. EXECUTING MODFLOW-2005
                         D. TESTING
                         E. COMPILING


A. DISTRIBUTION FILE

The following distribution file is for use on personal computers:

         mf2005v1_11_00.zip

The distribution file contains:

          Compiled runfiles and source code for MODFLOW-2005.
          Supplementary MODFLOW-2005 documentation in PDF and text files.
          Test data sets.

The distribution file is a compressed zip file. The following directory
structure is incorporated in the zip file:

 |
 |--mf2005.1_11
    |--bin            ; MODFLOW-2005 executables for personal computers
    |--doc            ; Documentation files
       |MF2005convert ; Documentation of package conversions for MODFLOW-2005
       |Updates       ; Revisions and enhancements to MODFLOW-2005
    |--src            ; MODFLOW-2005 source code for use on any computer
       |hydprograms   ; Source for hydrograph post processing program
       |mnw1to2       ; Source for program to convert MNW1 data files to MNW2
    |--test-run       ; Input data to run verification tests
    |--test-out       ; Output files from running the tests

The installation instructions assume that the files have been extracted from
the zip file into directory C:\WRDAPP, maintaining the above structure.

It is recommended that no user files are kept in the mf2005.1_11 directory
structure.  If you do plan to put your own files in the mf2005.1_11
directory structure, do so only by creating additional subdirectories.

Included in directory mf2005.1_11\doc are various documentation files.  Some
of them are Portable Document Format (PDF) files. The PDF files are readable
and printable on various computer platforms using Acrobat Reader from Adobe.
The Acrobat Reader is freely available from the following World Wide Web
site:
      http://www.adobe.com/


B. INSTALLING

To make the executable versions of MODFLOW-2005 accessible from any
directory, the directory containing the executables (mf2005.1_11\bin)
should be included in the PATH environment variable.  Also, if a
prior release of MODFLOW-2005 is installed on your system, the
directory containing the executables for the prior release should
be removed from the PATH environment variable.

As an alternative, the executable files, mf2005.exe and mf2005dbl.exe,
in the mf2005.1_11\bin directory can be copied into a directory already
included in the PATH environment variable.

       HOW TO ADD TO THE PATH ENVIRONMENT VARIABLE
                 WINDOWS 7 SYSTEMS
             
From the Start menu, select Control Panel.  Select System and Security,
and within that screen choose the System option. Then select the Advanced
System Settings option.  Select the Environment Variables button.  In the
System Variables pane, select the PATH variable followed by Edit.  In the
Edit window, add ";C:\WRDAPP\mf2005.1_11\bin" to the end of the Variable
Value (ensure that the current contents of the User Value are not deleted)
and click OK. Click OK in the Environment Variables window and then exit
from the control panel windows.  Initiate and use a new Windows Command
window.

       HOW TO ADD TO THE PATH ENVIRONMENT VARIABLE
                  WINDOWS XP SYSTEMS
             
From the Start menu, select Settings and then Control Panel.  Double click
System and select the Advanced tab.  Click on Environment Variables.  If
a PATH user variable already is defined, click on it in the User Variables
pane, then click Edit.  In the Edit User Variable window, add
";C:\WRDAPP\mf2005.1_11\bin" to the end of the Variable Value (ensure that
the current contents of the User Value are not deleted) and click OK.  If
a PATH user variable is not already defined in the User variables pane of
the Environment Variables window, click New.  In the New User Variable
window, define a new variable PATH as shown above.  Click OK.  Click OK
in the Environment Variables window and again in the System Properties
window.  Initiate and use a new Windows Command window.

       HOW TO ADD TO THE PATH ENVIRONMENT VARIABLE
                 WINDOWS VISTA SYSTEMS
             
From the Start menu, select Settings and then Control Panel.  Select
System & Maintenance followed by System.  Choose the Advanced System
option.  Select the Settings Task, and then select the Environmental
Variables button.  In the System Variables pane, select the PATH
variable followed by Edit.  In the Edit window, add
";C:\WRDAPP\mf2005.1_11\bin" to the end of the Variable Value (ensure
that the current contents of the User Value are not deleted) and click
OK. Click OK in the Environment Variables window and then exit from the
control panel windows.  Initiate and use a new Windows Command window.



C. EXECUTING MODFLOW-2005

Two MODFLOW-2005 runfiles for use on personal computers are provided. 
mf2005.exe is like the version that has been provided in all prior
versions of MODFLOW-2005.  It uses mixed single and double precision for
computations and internal data storage, which was determined to be useful
for a wide range of simulations.  There are situations in which the mixed
precision is inadequate, which can be indicated by difficulty attaining
solver convergence or poor budget error.  Accordingly, a runfile that
uses full double precision is provided -- mf2005dbl.exe. If mixed
precision is suspected of causing problems in a simulation, the same
simulation can be run using the full double precision runfile.  Input for
the two runfiles is the same.  In fact the source code is identical for
both.  The double precision runfile is created by using a compiler option
that raises the precision of single precision numbers to double precision.

The penalty for using full double precision is additional computer memory,
longer run times (depending on the computer), and unformatted (binary) files
that are doubled in size.  (Binary files are used for saving head, drawdown,
and budget data.) This penalty is frequently not very significant.  Typical
computers have adequate memory to run most double precision simulations, are
nearly as fast performing double precision as mixed precision, and have
abundant disk space for storing binary output files.

After the executable files in the mf2005.1_11\bin directory are installed
in a directory that is included in your PATH, MODFLOW-2005 is initiated in
a Windows Command-Prompt window using one of the following commands:

          mf2005 [Fname]
or
          mf2005dbl [Fname]

The optional Fname argument is the name file.  If no argument is used,
the user is prompted to enter the name file.  If the name file ends in
".nam", then the file name can be specified without including ".nam". 
For example, if the name file is named abc.nam, then the simulation can
be run using mixed precision by entering:

          mf2005 abc

The data arrays in MODFLOW-2005 are dynamically allocated, so models
are not limited by hard-coded array limits. However, it is best to have
enough random-access memory (RAM) available to hold all of the required
data.  If there is less available RAM than this, the program will use
virtual memory, but this slows computations significantly.

Some of the files written by MODFLOW are unformatted files.  The structure
of these files depends on the precision of the data in the program,
the compiler, and options in the Fortran write statement.  Any program
that use the unformatted files produced by MODFLOW must read the files
in the same way they were written. For example, Zonebudget and Modpath
use unformatted budget files produced by MODFLOW.  Current versions of
Zonebudget and Modpath automatically detect the precision of the data in
unformatted files and the runfiles provided by the USGS are compatible
with the structure of the unformatted files produced by this release of
MODFLOW-2005.

Another example of unformatted files is head files that are generated by
one MODFLOW simulation and used in a following simulation as initial
heads.  Both simulations must be run using an executable version of
MODFLOW that uses the same unformatted file structure.  MODFLOW does
not automatically detect precision of the data in these files, so both
simulations must be run using a runfile having the same precision.

This issue of unformatted files is described here so that users will
be aware of the possibility of problems caused by unformatted files. 
Older versions of MODFLOW executables provided by the U.S. Geological
Survey (USGS) may produce unformatted files with a different structure.
The current form of unformatted file has been used in USGS MODFLOW
executables starting with version 1.2 of MODFLOW-2000.


D. TESTING

Test data sets are provided to verify that MODFLOW-2005 is correctly
installed and running on the system.  The tests may also be looked
at as examples of how to use the program.  The directory
MF2005.1_11\test-run contains the input data for running each test. 
Directory MF2005.1_11\test-out contains the output files from running
each test. The tests are described in the file problems.txt.

The directory MF2005.1_11\test-run can be used to conveniently run the
tests without destroying the original results in the MF2005.1_11\test-out
directory.  The test-run directory contains MODFLOW name files, which end
with ".nam", for running the tests.  Each test can be run by entering the
name file for the test when executing MODFLOW-2005.  MODFLOW-2005 should
be run in a command-prompt window with the current directory being the
test-run directory.  The output files that are created in the test-run
directory can then be compared to those in MF2005.1_11\test-out.


E. COMPILING

The executable files provided in MF2005.1_11\bin were created using the Intel
Visual Fortran 13.1 and Microsoft Visual C++ .NET compilers.  Although
executable versions of the program are provided, the source code is provided
in the mf2005.1_11\src directory so that MODFLOW can be recompiled if
necessary.  However, the USGS cannot provide assistance to those compiling
MODFLOW. In general, the requirements are a Fortran compiler, a compatible
C compiler, and the knowledge of using the compilers.

The C compiler is used for the GMG solver.  If a compatible C compiler is
not available, the GMG solver can be removed so that only a Fortran compiler
is required.  File Nogmg.txt in the src directory contains instructions for
removing GMG from MODFLOW.
