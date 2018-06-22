C  MNW1to2 -- translate MNW1 input data to MNW2 input data
      MODULE GWFMNWMODULE
        INTEGER,          SAVE         :: MXMNW,NW, IWL2CB, KSPREF
        INTEGER,          SAVE         :: IWELPT, NOMOITER,IDEFTYP
        DOUBLE PRECISION, SAVE         :: PLOSS
        INTEGER,          SAVE,DIMENSION(3)             :: IOWELL2
        CHARACTER(LEN=200), SAVE :: MNWNAME
C
C  MNW1 data
        CHARACTER(LEN=32),SAVE,DIMENSION(:),    POINTER :: MNWSITE
        INTEGER, SAVE,DIMENSION(:), POINTER:: IL,IR,IC,IWGRP,ICUT
        REAL,    SAVE,DIMENSION(:), POINTER:: Q,QWVAL,RW,SKIN,HLIM,HREF
        REAL,    SAVE,DIMENSION(:), POINTER:: C,QCUT,QFRCMN,QFRCMX
        INTEGER, SAVE,DIMENSION(:), POINTER:: IWNUM,IWBEG,IWEND,LOSTYP1
C  MNW2 static data for a well
        PARAMETER (MX2=10000,MXLAY=50,MXPER=100)
        INTEGER, SAVE  :: NW2
        CHARACTER(LEN=32),SAVE,DIMENSION(MX2)::MNW2SITE
        INTEGER, SAVE,DIMENSION(MX2)         :: LOSTYP2,IHLIM2
        INTEGER, SAVE,DIMENSION(MXLAY,MX2)   :: IR2,IC2
C  MNW2 static data for each cell in a well
        INTEGER, SAVE,DIMENSION(MXLAY+1,MX2) :: IL2
        REAL,    SAVE,DIMENSION(MXLAY,MX2)   :: RW2,B2,C2
C  MNW2 transient data for a well
        INTEGER, SAVE,DIMENSION(MXPER)    :: ITMPPER
        INTEGER, SAVE,DIMENSION(MX2,MXPER):: IWNUM2,ICUT2
        REAL,    SAVE,DIMENSION(MX2,MXPER):: Q2,HLIM2,QFRCMN2,QFRCMX2
      END MODULE GWFMNWMODULE
C
c-------------------------------------------------------------------------
c
c     ******************************************************************
c     ******************************************************************
c
c        specifications:
c     ------------------------------------------------------------------
      USE GLOBAL,      ONLY: IOUT,NCOL,NROW,NLAY,NPER,NODES,NIUNIT,IUNIT
      USE GWFMNWMODULE
C
      CHARACTER*4 CUNIT(NIUNIT)
      DATA CUNIT/'BCF6', 'WEL ', 'DRN ', 'RIV ', 'EVT ', '    ', 'GHB ',  !  7
     &           'RCH ', 'SIP ', 'DE4 ', '    ', 'OC  ', 'PCG ', 'lmg ',  ! 14
     &           'gwt ', 'FHB ', 'RES ', 'STR ', 'IBS ', 'CHD ', 'HFB6',  ! 21
     &           'LAK ', 'LPF ', 'DIS ', '    ', 'PVAL', '    ', 'HOB ',  ! 28
     &           '    ', '    ', 'ZONE', 'MULT', 'DROB', 'RVOB', 'GBOB',  ! 35
     &           '    ', 'HUF2', 'CHOB', 'ETS ', 'DRT ', '    ', 'GMG ',  ! 42
     &           'HYD ', 'SFR ', '    ', 'GAGE', 'LVDA', '    ', 'LMT6',  ! 49
     &           'MNW1', '    ', '    ', 'KDEP', 'SUB ', 'UZF ', 'gwm ',  ! 56
     &           'SWT ', 'cfp ', '    ', '    ', '    ', '    ', 'nrs ',  ! 63
     &           37*'    '/
c     ------------------------------------------------------------------
      INTRINSIC ABS
      INTEGER, EXTERNAL :: IFRL
      EXTERNAL NCREAD, UPCASE, QREAD
c     ------------------------------------------------------------------
c     Arguments
c     ------------------------------------------------------------------
      INTEGER :: In,KPER
      CHARACTER(LEN=200) :: Fname
c     ------------------------------------------------------------------
c     Local Variables
c     ------------------------------------------------------------------
      REAL :: bs
      INTEGER :: ierr, io, iok, jf, ke, kf, ki, kio
      DOUBLE PRECISION :: rn(25)
      CHARACTER(LEN=256) :: txt, tx2
      INTEGER NC
      CHARACTER*80 HEADNG(2)
c     ------------------------------------------------------------------
c     Static Variables
c     ------------------------------------------------------------------
      CHARACTER(LEN=6) :: ftag(3)
      INTEGER :: icf(3)
      DATA ftag/'WEL1  ', 'BYNODE', 'QSUM  '/
      DATA icf/4, 6, 4/
c     ------------------------------------------------------------------
      IOUT=100
      OPEN(UNIT=IOUT,FILE='mnw1to2.lst')
C
      IN=99
C
C3------GET THE NAME OF THE NAME FILE
      CALL GETNAMFIL(FNAME)
C
C4------OPEN NAME FILE.
      OPEN (UNIT=IN,FILE=FNAME,STATUS='OLD')
      NC=INDEX(FNAME,' ')
      WRITE(*,490)' Using NAME file: ',FNAME(1:NC)
  490 FORMAT(A,A)
      CALL GWF2BAS7AR(IN,CUNIT,24,31,32,12,HEADNG,26)
      IF(IUNIT(23).GT.0) CALL GWF2LPF7AR(IUNIT(23))
      IF(IUNIT(1).GT.0) CALL GWF2BCF7AR(IUNIT(1))
      NODES=NCOL*NROW*NLAY
      IF(NPER.GT.MXPER) THEN
        WRITE(*,*) 'EXCEEDED STRESS-PERIOD LIMIT -- ',MXPER
        STOP
      END IF
C
      IN=IUNIT(50)
      IF(IN.LE.0) THEN
        WRITE(IOUT,*) 'MNW1 input file is not included in the Name File'
        STOP
      END IF
c
      IOWELL2(1) = 0
      IOWELL2(2) = 0
      IOWELL2(3) = 0
c
c1------identify package and initialize NW
      WRITE (IOUT, 9001) In
 9001 FORMAT (/, ' MNW7 -- MULTI-NODE WELL PACKAGE, VERSION 7,', 
     +        ' 11/07/2005.', /, '    INPUT READ FROM UNIT', i4)
      NW = 0
c
c2------read max number of wells and
c2------unit or flag for cell-by-cell flow terms.
      CALL NCREAD(In, txt, ierr)
      CALL UPCASE(txt)
c
      ki = INDEX(txt, 'REF')
      IF ( ki.GT.0 ) THEN
        tx2 = txt(ki:256)
        CALL QREAD(rn, 1, tx2, ierr)
        IF ( ierr.EQ.0 ) KSPREF = IFRL(rn(1))
        txt(ki:256) = '                                '
      ELSE
        KSPREF = 1
      ENDIF
c
      CALL QREAD(rn, 4, txt, ierr)
      MXMNW = IFRL(rn(1))
      IWL2CB = 0
      IF ( ierr.LE.2 ) IWL2CB = IFRL(rn(2))
      IWELPT = 0
      IF ( ierr.EQ.1 ) IWELPT = IFRL(rn(3))
      NOMOITER = 9999
      IF ( ierr.EQ.0 ) NOMOITER = IFRL(rn(4))
c
      WRITE (IOUT, 9002) MXMNW
      IF ( IWL2CB.GT.0 ) WRITE (IOUT, 9003) IWL2CB
      IF ( IWL2CB.LT.0 ) WRITE (IOUT, 9004)
      WRITE (IOUT, 9005) KSPREF
      WRITE (IOUT, 9006) NOMOITER
 9002 FORMAT (' MAXIMUM OF', i5, ' WELLS')
 9003 FORMAT (' CELL-BY-CELL FLOWS WILL BE RECORDED ON UNIT', i3)
 9004 FORMAT (' CELL-BY-CELL FLOWS WILL BE PRINTED WHEN ICBCFL NOT 0')
 9005 FORMAT ('  The heads at the beginning of SP:', i4, 
     +        ' will be the default reference elevations.', /)
 9006 FORMAT (' Flow rates will not be estimated after the', i4, 
     +        'th iteration')
c
c   Define well model to be used
      CALL NCREAD(In, txt, ierr)
      CALL UPCASE(txt)
      PLOSS = 0.0D0   !!  Default use of Skin so linear loss varies with T
      IDEFTYP=0
      IF ( INDEX(txt, 'LINEAR').GT.0 ) THEN
        PLOSS = 1.0D0 !!  ADD THIS LINE to make sure that the power term is 1 for the linear model
        ki = INDEX(txt, ':') + 1
        tx2 = txt(ki:256)
        CALL QREAD(rn, 1, tx2, ierr)
        IF ( ierr.EQ.0 ) PLOSS = rn(1)
c   Add error checking to shut down MODFLOW
        bs = 3.6           !!   Maximum limit on power term
        IF ( PLOSS.GT.bs ) THEN
          WRITE (*, *) 'Power term of', PLOSS, ' exceeds maximum of', bs
          WRITE (IOUT, *) 'Power term of', PLOSS, ' exceeds maximum of',
     +                    bs
C
          STOP
        ENDIF
        IDEFTYP=1
      ENDIF
c
c   Test for a specified PREFIX NAME  for time series output from MNW7OT
      CALL NCREAD(In, txt, ierr)
      tx2 = txt
      CALL UPCASE(tx2)
      kf = INDEX(tx2, 'PREFIX:')
      IF ( kf.GT.0 ) THEN
        MNWNAME = txt(kf+7:256)
        ke = INDEX(MNWNAME, ' ')
        MNWNAME(ke:200) = '               '
        tx2 = MNWNAME
        CALL UPCASE(tx2)
        IF ( INDEX(tx2, 'FILEPREFIX').GT.0 ) THEN
          MNWNAME = Fname
          ke = INDEX(MNWNAME, '.')
          MNWNAME(ke:200) = '               '
        ENDIF
      ELSE
        MNWNAME = 'OUTput_MNW'
        BACKSPACE (In)
      ENDIF
c
c     Test for creation of a WEL1 package and auxillary output files
c
      iok = 1
      DO WHILE ( iok.EQ.1 )
        CALL NCREAD(In, txt, ierr)
        tx2 = txt
        CALL UPCASE(tx2)
        kf = INDEX(tx2, 'FILE:')
        IF ( kf.GT.0 ) THEN
          kio = 0
          jf = 0
          DO WHILE ( kio.EQ.0 .AND. jf.LT.3 )
            jf = jf + 1
            kio = INDEX(tx2, ftag(jf)(1:icf(jf)))
            IF ( kio.GT.0 ) THEN
              tx2 = txt(kio+1+icf(jf):256)
              CALL QREAD(rn, 1, tx2, ierr)
              IF ( ierr.EQ.0 ) THEN
                IOWELL2(jf) = IFRL(rn(1))
c            OC over ride is ALLTIME
                IF ( INDEX(tx2, 'ALLTIME').GT.0 ) IOWELL2(jf)
     +               = -IOWELL2(jf)
c            Find and use file name
                tx2 = txt(kf+5:256)
                kf = INDEX(tx2, ' ') - 1
                CLOSE (ABS(IOWELL2(jf)))
                OPEN (ABS(IOWELL2(jf)), FILE=tx2(1:kf))
                WRITE (tx2(253:256), '(i4)') ABS(IOWELL2(jf))
                txt = ' A '//ftag(jf)
     +                //' data input file will be written'//' to '//
     +                tx2(1:kf)//' on unit '//tx2(253:256)
                WRITE (IOUT, '(/1x,a79)') txt
                IF ( jf.EQ.1 )
     +          WRITE (ABS(IOWELL2(jf)),'(3i10)') MXMNW, IWL2CB, IWELPT
              ENDIF
            ENDIF
          ENDDO
        ELSE
          BACKSPACE (In)
          iok = 0
        ENDIF
      ENDDO
c
c
      ALLOCATE (MNWSITE(MXMNW))
      ALLOCATE (IL(MXMNW),IR(MXMNW),IC(MXMNW),IWGRP(MXMNW),ICUT(MXMNW))
      ALLOCATE (Q(MXMNW),QWVAL(MXMNW),RW(MXMNW),SKIN(MXMNW),HLIM(MXMNW))
      ALLOCATE (HREF(MXMNW),C(MXMNW),QCUT(MXMNW),QFRCMN(MXMNW))
      ALLOCATE (QFRCMX(MXMNW))
      ALLOCATE (IWNUM(MXMNW),IWBEG(MXMNW),IWEND(MXMNW),LOSTYP1(MXMNW))
c
c
c7------Read stress period data
      NW2=0
      DO 500 KPER=1,NPER
      CALL GWF2MNW7RP(IN,KPER)
500   CONTINUE
C
C  Write MNW2 data
      CALL MNW2WRITE
C
      STOP
      END
c
      SUBROUTINE GWF2MNW7RP(In, Kper)
c     ******************************************************************
c     read new well locations, stress rates, well char., and limits
c     ******************************************************************
c
c        specifications:
c     ------------------------------------------------------------------
      USE GLOBAL,      ONLY:NODES,NCOL,NROW,NLAY,IOUT,IUNIT
      USE GWFMNWMODULE
c     ------------------------------------------------------------------
c     Arguments
c     ------------------------------------------------------------------
      INTEGER, INTENT(IN) :: Kper
      INTEGER, INTENT(INOUT) :: In
c     ------------------------------------------------------------------
c     Local Variables
c     ------------------------------------------------------------------
      CHARACTER(LEN=256) :: LINE
      CHARACTER*100 CBUF
      CHARACTER*32 STMP
      CHARACTER*10 LOSNAM(0:4)
      DATA LOSNAM/'NONE','THIEM','SKIN','GENERAL','SPECIFYcwc'/
      INTEGER, SAVE ::IDDMES=0
c     ------------------------------------------------------------------
C
c1------read itmp(number of wells or flag saying reuse well data)
10    READ(IN,'(A)') LINE
      IF(LINE(1:1) .EQ.'#') GO TO 10
C
C
      LLOC=1
      CALL URWORD(LINE,LLOC,ISTART,ISTOP,2,ITMP,R,IOUT,IN)
      IF(ITMP.GT.MX2) THEN
        WRITE(IOUT,*) 'Too many MNW1 wells -- max. is',MX2
        STOP
      END IF
      ITMPPER(KPER)=ITMP
c
      IF ( itmp.LT.0 ) THEN
c        if itmp less than zero reuse data. print message and return.
        WRITE (IOUT, 9001)
 9001   FORMAT (1X,/1X,'REUSING MNW7  FROM LAST STRESS PERIOD')
        RETURN
      ELSE
c  If itmp > 0,  Test if wells are to replace old ones or be added.
c
        CALL URWORD(LINE,LLOC,ISTART,ISTOP,1,I,R,IOUT,IN)
        IF(LINE(ISTART:ISTOP).NE.'ADD') NW=0
      END IF
c
c   return if there are no wells to read ........
      IF ( itmp.EQ.0 ) RETURN
c
c   Read additional well info
      IMSTART=1
      NM=0
      DQFRCMN=0.
      DQFRCMX=0.
      ICUTDEF=0
      DO 500 m = 1, itmp
200     READ(IN,'(A)') LINE
        IF(LINE(1:1).EQ.'#') GO TO 200
        CALL UPCASE(LINE)
        NW=NW+1
c  If NW>mxmnw.  print message. stop.
        IF ( NW.GT.MXMNW ) THEN
          WRITE (IOUT, 9002) NW, MXMNW
 9002     FORMAT (1X,/
     1     1X,'NW(', i4, ') IS GREATER THAN mxmnw(', i4, ')')
          STOP
        ENDIF
C
C  Check for some of keywords -- any order is accepted here
C
C  CP:, QCUT:, and Q-%CUT
        C(NW)=0.
        QFRCMN(NW)=DQFRCMN
        QFRCMX(NW)=DQFRCMX
        ICUT(NW)=ICUTDEF
        ICP=INDEX(LINE,'CP:')
        IF(ICP.GT.0) THEN
          LINE(ICP:ICP+2)=' '
          CALL URWORD(LINE,ICP,ISTART,ISTOP,3,IDUM,C(NW),IOUT,IN)
          LINE(ISTART:ISTOP)=' '
        END IF
        IQCUT=INDEX(LINE,'QCUT:')
        IF(IQCUT.GT.1) THEN
          LINE(IQCUT:IQCUT+4)=' '
          CALL URWORD(LINE,IQCUT,ISTART,ISTOP,3,IDUM,QFRCMN(NW),IOUT,IN)
          LINE(ISTART:ISTOP)=' '
          CALL URWORD(LINE,IQCUT,ISTART,ISTOP,3,IDUM,QFRCMX(NW),IOUT,IN)
          LINE(ISTART:ISTOP)=' '
          IDEF=INDEX(LINE,'DEFAULT')
          IF(IDEF.GT.0) THEN
            LINE(IDEF:IDEF+6)=' '
            DQFRCMN=QFRCMN(NW)
            DQFRCMX=QFRCMX(NW)
            ICUTDEF=1
          END IF
          ICUT(NW)=1
        END IF
        IQCUT=INDEX(LINE,'Q-%CUT:')
        IF(IQCUT.GT.1) THEN
          LINE(IQCUT:IQCUT+6)=' '
          CALL URWORD(LINE,IQCUT,ISTART,ISTOP,3,IDUM,QFRCMN(NW),IOUT,IN)
          LINE(ISTART:ISTOP)=' '
          CALL URWORD(LINE,IQCUT,ISTART,ISTOP,3,IDUM,QFRCMX(NW),IOUT,IN)
          LINE(ISTART:ISTOP)=' '
          IDEF=INDEX(LINE,'DEFAULT')
          IF(IDEF.GT.0) THEN
            LINE(IDEF:IDEF+6)=' '
            DQFRCMN=QFRCMN(NW)
            DQFRCMX=QFRCMX(NW)
            ICUTDEF=-1
          END IF
          ICUT(NW)=-1
        END IF
C
C  If there is a site name, get the name and strip this off the end.
        ISITE=INDEX(LINE,'SITE:')
        IF(ISITE.GT.0) THEN
           CBUF=LINE(ISITE+5:)
           MNWSITE(NW)=ADJUSTL(CBUF)
           LINE(ISITE:256)=' '
        ELSE
           MNWSITE(NW)=' '
        END IF
C
C  Parse the initial 4 non-keyword data values for MNW cell
        LLOC=1
        CALL URWORD(LINE,LLOC,ISTART,ISTOP,2,IL(NW),R,IOUT,IN)
        CALL URWORD(LINE,LLOC,ISTART,ISTOP,2,IR(NW),R,IOUT,IN)
        CALL URWORD(LINE,LLOC,ISTART,ISTOP,2,IC(NW),R,IOUT,IN)
        CALL URWORD(LINE,LLOC,ISTART,ISTOP,3,IDUM,Q(NW),IOUT,IN)
C
C  Check for MN or MULTI
        LOCSAV=LLOC
        CALL URWORD(LINE,LLOC,ISTART,ISTOP,1,IDUM,RDUM,IOUT,IN)
        IF(LINE(ISTART:ISTOP).EQ.'MN') THEN
          LINE(ISTART:ISTOP)=' '
          IWNUM(NW)=NM
          IMSTART=NW+1
        ELSE IF(LINE(ISTART:ISTOP).EQ.'MULTI') THEN
          LINE(ISTART:ISTOP)=' '
C  save the Multiple-well group
          NM=NW-IMSTART+1
          DO 15 NN=IMSTART,NW
          IWNUM(NN)=NM
15        CONTINUE
          IMSTART=NW+1
        ELSE
c  No MN or MULTI flag -- Save the cell as a new single=cell well
          NM=NM+1
          IWNUM(NW)=NM
          LLOC=LOCSAV
        END IF
C
        QWVAL(NW)=0.
        RW(NW)=0.
        SKIN(NW)=0.
        HLIM(NW)=0.
        HREF(NW)=0.
        IWGRP(NW)=0
        CALL URWORD(LINE,LLOC,ISTART,ISTOP,3,IDUM,QWVAL(NW),IOUT,IN)
        CALL URWORD(LINE,LLOC,ISTART,ISTOP,3,IDUM,RW(NW),IOUT,IN)
C  SKIN -- there might be nothing there
        CALL URWORD(LINE,LLOC,ISTART,ISTOP,3,IDUM,SKIN(NW),-1,IN)
        L=LEN(LINE)
        IF(LINE(L:L).EQ.'E') GO TO 499
C  Look for DD before HLIM & HREF
        IDD=0
        LOCSAV=LLOC
        CALL URWORD(LINE,LLOC,ISTART,ISTOP,1,IDUM,RDUM,IOUT,IN)
        IF(LINE(ISTART:ISTOP).EQ.'DD') THEN
          IDD=1
        ELSE
          LLOC=LOCSAV
        END IF
C  HLIM & HREF -- there might be nothing more
        CALL URWORD(LINE,LLOC,ISTART,ISTOP,3,IDUM,HLIM(NW),-1,IN)
        L=LEN(LINE)
        IF(LINE(L:L).EQ.'E' .OR. (ISTART.EQ.L .AND. ISTOP.EQ.L)) THEN
C  Use HLIM=-1E30 as a flag to indicate HLIM is unspecified.
          HLIM(NW)=-1.E30
          GO TO 499
        END IF
        CALL URWORD(LINE,LLOC,ISTART,ISTOP,3,IDUM,HREF(NW),IOUT,IN)
C  Look for DD after HLIM & HREF
        LOCSAV=LLOC
        CALL URWORD(LINE,LLOC,ISTART,ISTOP,1,IDUM,RDUM,IOUT,IN)
        IF(LINE(ISTART:ISTOP).EQ.'DD') THEN
          IDD=1
        ELSE
          LLOC=LOCSAV
        END IF
        IF(IDD.EQ.1) THEN
          IF(IDDMES.EQ.0) THEN
            WRITE(IOUT,*)
     1  '  DD flag -- MNW2 does not implement the check for HREF>HNEW'
            WRITE(*,*)
     1      'Do you want HLIM computed based on HREF (Y/N) ?'
            READ(*,'(A)') CBUF
            IF(CBUF(1:1).EQ.'Y' .OR. CBUF(1:1).EQ.'y') THEN
              IDDMES=1
              WRITE(*,*) 'HLIM computed from HREF when DD is specified'
              WRITE(IOUT,*)
     1                   'HLIM computed from HREF when DD is specified'
            ELSE
              IDDMES=-1
              WRITE(*,*) 'HLIM deactivated when DD is specified'
              WRITE(IOUT,*) 'HLIM deactivated when DD is specified'
            END IF
          END IF
C
          IF(IDDMES.EQ.1) THEN
            IF(Q(NW).GT.0) THEN
              HLIM(NW)=HREF(NW)+HLIM(NW)
            ELSE IF(Q(NW).LT.0.) THEN
              HLIM(NW)=HREF(NW)-HLIM(NW)
            END IF
          ELSE
C  Deactivate DD at request of user
            HLIM(NW)=-1.E30
          END IF
        END IF
        CALL URWORD(LINE,LLOC,ISTART,ISTOP,2,IWGRP(NW),RDUM,IOUT,IN)
C
C  Identify the loss type
499   IF(RW(NW).EQ.0.0) THEN
        LOSTYP1(NW)=0
      ELSE IF(RW(NW).LT.0.0) THEN
        LOSTYP1(NW)=4
      ELSE IF(IDEFTYP.EQ.0) THEN
        IF(SKIN(NW).LE.0.) THEN
          LOSTYP1(NW)=1
        ELSE
          LOSTYP1(NW)=2
        END IF
      ELSE
        LOSTYP1(NW)=3
      END IF
C
C  End of input loop for stress period
500   CONTINUE
C
C  Process MNW site names
      NM=1
      MSTART=1
C  Find the start of a new well and then go back to find the name of 
C  the prior well
      IF(NW.GT.1) THEN
        DO 550 M=2,NW
        IF(IWNUM(M).NE.NM) THEN
          MEND=M-1
          DO 520 MM=MSTART,MEND
            IF(MNWSITE(MM).NE.' ') THEN
              STMP=MNWSITE(MM)
              GO TO 525
            END IF
520       CONTINUE
C
C  Site name is blank -- create a name
          CALL NAMGEN(MSTART,MEND,STMP)
C
525       DO 526 MM=MSTART,MEND
          MNWSITE(MM)=STMP
526       CONTINUE
          IWBEG(IWNUM(M-1))=MSTART
          IWEND(IWNUM(M-1))=MEND
          NM=IWNUM(M)
          MSTART=M
        END IF
550     CONTINUE
      END IF
C
C  Set the site name for the last well
      MEND=NW
      DO 560 MM=MSTART,MEND
        IF(MNWSITE(MM).NE.' ') THEN
          STMP=MNWSITE(MM)
          GO TO 575
        END IF
560   CONTINUE
      CALL NAMGEN(MSTART,MEND,STMP)
C
575   DO 586 MM=MSTART,MEND
      MNWSITE(MM)=STMP
586   CONTINUE
      IWBEG(IWNUM(NW))=MSTART
      IWEND(IWNUM(NW))=MEND
C
C   Write input to iout file
      WRITE(IOUT, '(1X,/,10x,i5," MNW NODES")') NW
      WRITE(IOUT,9003)
 9003 FORMAT ('MNW1 No. MNW2 No. Lay   Row   Col    Stress  ', 
     +     'LOSS TYPE        Rw       SKIN (or B)    C     ',
     +  '   WL Limit  ICUT  Min-Qoff    Min-Qon     Site Identifier')
      DO 600 M=1,NW
      NW=M
      WRITE(IOUT,9007) NW,IWNUM(NW),IL(NW),IR(NW),IC(NW),Q(NW),
     1 LOSNAM(LOSTYP1(NW)),RW(NW),SKIN(NW),C(NW),HLIM(NW),ICUT(NW),
     2 QFRCMN(NW),QFRCMX(NW),MNWSITE(NW)
9007  FORMAT(1X,I6,I9,I5,2I6,1P,E12.4,2X,A,4E12.4,I5,2E12.4,2X,A)
600   CONTINUE
      ITMPPER(KPER)=IWNUM(NW)
C
C  WRITE MNW wells
      WRITE(IOUT,*)
      WRITE(IOUT,*) IWNUM(NW),' WELLS:'
      DO 700 M=1,IWNUM(NW)
      IF(LOSTYP1(IWBEG(M)).EQ.2) THEN
        DO 650 MM=IWBEG(M),IWEND(M)
        CALL GKSKIN(MM,SKIN(MM),RW(MM),SKINK2,RSKIN2,IUNIT(1),IUNIT(23),
     1               IL(MM),IR(MM),IC(MM))
        SKIN(MM)=SKINK2
        C(MM)=RSKIN2
650     CONTINUE
      END IF
700   CONTINUE
C
C  Check for consistent LOSTYP for each node in a MNW
C  stress period
      CALL LOSCHK(KPER,IWNUM(NW),IERR)
C
C  Check for unique name in
C  stress period
      CALL DUPCHK(KPER,IWNUM(NW),IERR)
C
C  Move wells to the MNW2 list
      CALL MOVEWELLS(KPER)
C
      RETURN
      END
      SUBROUTINE MOVEWELLS(KPER)
C     ******************************************************************
C     Move MNW1 data for 1 stress period to MNW2 data
C     ******************************************************************
      USE GLOBAL ,      ONLY: IOUT
      USE GWFMNWMODULE
C
      IF(ITMPPER(KPER).LE.0) RETURN
C
C  Existing wells.
      DO 500 M=1,ITMPPER(KPER)
C  Look for well in list
      CALL WELLFIND(M,IFOUND,M2)
      IF(IFOUND.EQ.0) THEN
C  Name does not match existing name -- add name to MNW2 list
        CALL ADDWELL(M,KPER)
        M2=NW2
      ELSE IF(IFOUND.EQ.1) THEN
C  Name matches current name, but Loss Type, # of cells, RW, B2, or C2
C  do not match -- generate a new name and look again.
        NC=LEN_TRIM(MNWSITE(IWBEG(M)))
        DO 50 NEW=1,26
        MNWSITE(IWBEG(M))(NC+1:NC+1)=CHAR(ICHAR('A')+NEW-1)
        CALL WELLFIND(M,IFOUND,M2)
        IF(IFOUND.EQ.0) THEN
          CALL ADDWELL(M,KPER)
          M2=NW2
          GO TO 100
        ELSE IF(IFOUND.EQ.2) THEN
          GO TO 100
        END IF
50      CONTINUE
        WRITE(IOUT,*) 'Unable to generate a unique name:',
     1             MNWSITE(IWBEG(M))
        STOP
      END IF
C
C  Add data to stress period list
100   M1=IWBEG(M)
      IWNUM2(M,KPER)=M2
      HLIM2(M,KPER)=HLIM(M1)
      ICUT2(M,KPER)=ICUT(M1)
      QFRCMN2(M,KPER)=QFRCMN(M1)
      QFRCMX2(M,KPER)=QFRCMX(M1)
      QTOT=0.
      DO 450 MN=IWBEG(M),IWEND(M)
      QTOT=QTOT+Q(MN)
450   CONTINUE
      Q2(M,KPER)=QTOT
C
500   CONTINUE
C
      RETURN
      END
      SUBROUTINE WELLFIND(M,IFOUND,M2)
C     ******************************************************************
C     Search for existing MNW2 well
C     ******************************************************************
      USE GWFMNWMODULE
C
      IFOUND=0
      IF(NW2.LE.0) RETURN
C
      DO 20 LOOK=1,NW2
        IF(MNWSITE(IWBEG(M)).EQ.MNW2SITE(LOOK)) THEN
          IF(LOSTYP1(IWBEG(M)).NE.LOSTYP2(LOOK)) GO TO 100
C  IHLIM2=0 and HLIM=-1.E30 are used to specify no head limit
C  IHLIM2=1 and HLIM not -1.E30 are used to specify that thers is a head limit
          IF(HLIM(IWBEG(M)).EQ.-1.E30 .AND. IHLIM2(LOOK).EQ.1) GO TO 100
          IF(HLIM(IWBEG(M)).NE.-1.E30 .AND. IHLIM2(LOOK).EQ.0) GO TO 100
          N2=IL2(MXLAY+1,LOOK)
          IF( (IWEND(M)-IWBEG(M)+1) .NE. N2 ) GO TO 100
          II=-1
          DO 10 LCELL=1,N2
            II=II+1
            IF(IR(IWBEG(M)+II)   .NE. IR2(LCELL,LOOK)) GO TO 100
            IF(IC(IWBEG(M)+II)   .NE. IC2(LCELL,LOOK)) GO TO 100
            IF(IL(IWBEG(M)+II)   .NE. IL2(LCELL,LOOK)) GO TO 100
            IF(RW(IWBEG(M)+II)   .NE. RW2(LCELL,LOOK)) GO TO 100
            IF(SKIN(IWBEG(M)+II) .NE. B2(LCELL,LOOK)) GO TO 100
            IF(C(IWBEG(M)+II)    .NE. C2(LCELL,LOOK)) GO TO 100
10        CONTINUE
C  Found a complete match -- name and data
          IFOUND=2
          M2=LOOK
          RETURN
        END IF
20    CONTINUE
C  Did not find a name match
      RETURN
C
C  Matches name, but different data for the well
100   IFOUND=1
      RETURN
C
      END
      SUBROUTINE ADDWELL(M,KPER)
C     ******************************************************************
C     Move MNW1 well M to the MNW2 list of wells.
C     ******************************************************************
      USE GLOBAL ,ONLY:  IOUT
      USE GWFMNWMODULE
C
C  Move well data
      NW2=NW2+1
      IF(NW2.GT.MX2) THEN
        WRITE(IOUT,*) 'Too many wells -- Max. is',MX2
        STOP
      END IF
      M1=IWBEG(M)
      MNW2SITE(NW2)=MNWSITE(M1)
      LOSTYP2(NW2)=LOSTYP1(M1)
      IHLIM2(NW2)=1
      IF(HLIM(M1).EQ.-1.E30) IHLIM2(NW2)=0
C
C  Move cell data
        IF( (IWEND(M)-IWBEG(M)+1) .GT.MXLAY) THEN
          WRITE(IOUT,*) 'Well screened in too many layers -- max. is',
     1              MXLAY
          STOP
        END IF
        N=0
        DO 10 MN=IWBEG(M),IWEND(M)
        N=N+1
        IR2(N,NW2)=IR(MN)
        IC2(N,NW2)=IC(MN)
        IL2(N,NW2)=IL(MN)
        RW2(N,NW2)=RW(MN)
        B2(N,NW2)=SKIN(MN)
        C2(N,NW2)=C(MN)
10      CONTINUE
        IL2(MXLAY+1,NW2)=N
C
      RETURN
      END
      SUBROUTINE GKSKIN(MM,SKIN1,RW1,SKINK2,RSKIN2,IUBCF,IULPF,
     1                  K,I,J)
C     ******************************************************************
C     Compute KSKIN and RSKIN from MNW1 SKIN and hydraulic data
C     ******************************************************************
      USE GLOBAL ,      ONLY: BOTM,LBOTM,CC,IOUT
      USE GWFBCFMODULE, ONLY: LAYCON,HY,TRPY
      USE GWFLPFMODULE,ONLY : LAYTYP,HK,CHANI,HANI
C
      IF(IUBCF.GT.0) THEN
        IF(LAYCON(K).EQ. 0 .OR. LAYCON(K).EQ.2) THEN
          THICK=BOTM(J,I,LBOTM(K)-1)-BOTM(J,I,LBOTM(K))
          X=CC(J,I,K)/THICK
        ELSE
          KB=0
          DO 200 KK=1,K
          IF(LAYCON(KK).EQ.1 .OR. LAYCON(KK).EQ.3) KB=KB+1
200       CONTINUE
          X=HY(J,I,KB)
        END IF
        Y=X*TRPY(K)
      ELSE IF(IULPF.GE.0) THEN
        X=HK(J,I,K)
        IF(CHANI(K).GT.0.) THEN
          Y=X*CHANI(K)
        ELSE
          KH=-CHANI(K)
          Y=X*HANI(J,I,KH)
        END IF
      ELSE
        WRITE(IOUT,*) 'BCF or LPF required to computer KSKIN and RSKIN'
        STOP
      END IF
      RSKIN2=RW1*2.0
      SKINK2=SQRT(X*Y)/((SKIN1/LOG(2.0))+1.0)
C
      RETURN
      END
      SUBROUTINE LOSCHK(KPER,NMW,IERR)
C     ******************************************************************
C     Check for consistent LOSS TYPE for nodes in each MNW
C     ******************************************************************
      USE GWFMNWMODULE
      USE GLOBAL  ,ONLY: IOUT
C
      IERR=0
      IF(NMW.EQ.0) RETURN
C
      DO 100 M=1,NMW
      IF(IWEND(M).EQ.IWBEG(M)) GO TO 100
      L=LOSTYP1(IWBEG(M))
      DO 99 MCHK=IWBEG(M)+1,IWEND(M)
      IF(LOSTYP1(MCHK).NE.L) THEN
         WRITE(IOUT,*) 'Loss type variation within a multi-node well:',
     1                  MNWSITE(MCHK)
         STOP
      END IF
99    CONTINUE
100   CONTINUE
C
      RETURN
      END
      SUBROUTINE DUPCHK(KPER,NMW,IERR)
C     ******************************************************************
C     Check for duplicate names within the wells of one stress period
C     ******************************************************************
      USE GWFMNWMODULE
      USE GLOBAL  ,ONLY: IOUT
      CHARACTER*20 SNAM
C
      IERR=0
      IF(NMW.EQ.0) RETURN
C
      DO 100 M=2,NMW
      SNAM=MNWSITE(IWBEG(M))
      DO 99 MCHK=1,M-1
      IF(MNWSITE(IWBEG(MCHK)).EQ.SNAM) THEN
         WRITE(IOUT,*) 'DUPLICATE MNW SITE NAME -- ',SNAM
         STOP
      END IF
99    CONTINUE
100   CONTINUE
C
      RETURN
      END
      INTEGER FUNCTION IFRL(R)
c     ******************************************************************
c     ******************************************************************
      IMPLICIT NONE
      INTRINSIC ABS
c Arguments
      DOUBLE PRECISION, INTENT(IN) :: R
c Local Variables
      INTEGER :: ip
c     ------------------------------------------------------------------
      ip = ABS(R) + 0.5D0
      IF ( R.LT.0.0D0 ) ip = -ip
      IFRL = ip
      END FUNCTION IFRL
c
      SUBROUTINE NCREAD(Io, Txt, Ierr)
c     ******************************************************************
c     NCREAD: reads lines of input and ignores lines that begin with a "#" sign.
c          All information after a ! is wiped from the input card.
c     ******************************************************************
      IMPLICIT NONE
      EXTERNAL UPCASE
c Arguments
      INTEGER, INTENT(INOUT) :: Io
      INTEGER, INTENT(OUT) :: Ierr
      CHARACTER(LEN=256), INTENT(OUT) :: Txt
c Local Variables
      INTEGER :: ioalt, ioflip, iohold, ki
      CHARACTER(LEN=128) :: afile
      CHARACTER(LEN=256) :: tx2
      DATA ioflip, ioalt/69, 69/
c     ------------------------------------------------------------------
      Ierr = 0
    5 READ (Io, '(a)', END=10) Txt
      IF ( Txt(1:1).EQ.'#' ) GOTO 5
c
      ki = INDEX(Txt, '!')
      IF ( ki.GT.0 )
     +  Txt(ki:256) = '                                                '
c
      tx2 = Txt
      CALL UPCASE(tx2)
c
c    Test for switching control to an auxillary input file
c
      ki = INDEX(Txt, ':')
      IF ( INDEX(tx2, 'REDIRECT').GT.0 .AND. ki.GT.0 ) THEN
        afile = Txt(ki+1:256)
        ki = INDEX(afile, '  ') - 1
        iohold = Io
        Io = ioflip
        ioflip = iohold
        OPEN (Io, FILE=afile(1:ki), STATUS='OLD', ERR=20)
        GOTO 5
      ENDIF
c
c    Test for returning io control from auxillary input to master input file
c
      IF ( INDEX(tx2, 'RETURN').GT.0 .AND.
     +     INDEX(tx2, 'CONTROL').GT.0 ) GOTO 10
c
      ki = INDEX(tx2, '<END>')
      IF ( ki.GT.0 ) THEN
        Ierr = 1
        Txt(ki+5:256) = '                                           '
      ENDIF
c
      IF ( INDEX(tx2, '<STOP>').GT.0 ) Ierr = 2
      RETURN
c
c    Report error in opening auxillary input file and stop
c
   20 WRITE (*, 25) afile
   25 FORMAT (/, '  ERROR opening auxillary input file', //,
     + '   The file:  ', a40, ' does not exist', /)
c
      STOP
c
   10 Txt(1:3) = 'EOF'
      IF ( Io.EQ.ioalt ) THEN
        CLOSE (Io)
        iohold = Io
        Io = ioflip
        ioflip = iohold
        GOTO 5
      ELSE
        Ierr = -1
      ENDIF
c
      END SUBROUTINE NCREAD
c
      SUBROUTINE QREAD(R, Ni, Ain, Ierr)
c     ******************************************************************
c     ******************************************************************
      IMPLICIT NONE
      INTRINSIC CHAR, INDEX
      INTEGER, PARAMETER :: MRNV=25
c Arguments
      DOUBLE PRECISION, INTENT(OUT), DIMENSION(MRNV) :: R
      INTEGER, INTENT(IN) :: Ni
      INTEGER, INTENT(OUT) :: Ierr
      CHARACTER(LEN=256), INTENT(IN) :: Ain
c Local Variables
      INTEGER :: i, istat, ki, n, nd
      CHARACTER(LEN=1) :: tab
      CHARACTER(LEN=8) :: rdfmt
      CHARACTER(LEN=256) :: a256
c     ------------------------------------------------------------------
      Ierr = 0
      tab = CHAR(9)           ! sets tab delimiter
c
c   r(ni+1) records the number of non-numeric entries that were attempted to be read as a number
c   r(ni+2) records the last column that was read from the card
c
      R(Ni+1) = -1.0D0
      a256 = Ain
      DO i = 1, 256
        IF ( a256(i:i).EQ.tab ) a256(i:i) = ' '
        IF ( a256(i:i).EQ.',' ) a256(i:i) = ' '
        IF ( a256(i:i).EQ.':' ) a256(i:i) = ' '
        IF ( a256(i:i).EQ.'=' ) a256(i:i) = ' '
      ENDDO
      n = 1
      i = 0
   11 R(Ni+1) = R(Ni+1) + 1.0D0
   10 i = i + 1
      IF ( i.GE.256 ) GOTO 15
      IF ( a256(i:i).EQ.' ' ) THEN
        a256(i:i) = '?'
        GOTO 10
      ENDIF
c
      ki = INDEX(a256, ' ') - 1
      nd = ki - i + 1
      rdfmt = '(F??.0) '
      WRITE (rdfmt(3:4), '(i2.2)') nd
CERB  Fix for bug that caused i to be incremented by only 1 position
CERB  each time the read statement returns an error.  This bug also
CERB  incremented r(ni+1) unnecessarily.  With Lahey-compiled code, the
CERB  buggy version would read a final E in a word (without returning an
CERB  error) as a zero.
CERB      read (a256(i:ki),rdfmt,err=11,end=10) r(n)
      READ (a256(i:ki), rdfmt, ERR=13, IOSTAT=istat) R(n)
   13 CONTINUE
      i = ki
      IF ( istat.GT.0 ) GOTO 11 ! PART OF BUG FIX -- ERB
      n = n + 1
      IF ( n.LE.Ni .AND. i.LT.256 ) GOTO 10
c
   15 n = n - 1
      Ierr = Ni - n
      R(Ni+2) = i
c
      END SUBROUTINE QREAD
      SUBROUTINE MNW2WRITE
C     ******************************************************************
C     WRITE MNW2 data
C     ******************************************************************
      USE GLOBAL ,ONLY:NPER
      USE GWFMNWMODULE
      CHARACTER*10 LOSNAM(0:4)
      DATA LOSNAM/'NONE','THIEM','SKIN','GENERAL','SPECIFYcwc'/
C
      IU=100
      OPEN(UNIT=IU,FILE='mnw1to2.mnw')
C
      WRITE(IU,'(A)') '#MNW2 data by mnw1to2 program'
      WRITE(IU,*) NW2,IWL2CB,
     1    '                             2     MNWMAX,IWL2CB,MNWPRNT'
C
      LCUT=0
      DO 100 N=1,NW2
C  Item 2a
      IF(LEN_TRIM(MNW2SITE(N)).GT.20) THEN
        LCUT=LCUT+1
        WRITE(MNW2SITE(N)(17:20),'(I4.4)') LCUT
      END IF
      WRITE(IU,107) MNW2SITE(N)(1:20),IL2(MXLAY+1,N),
     1           '               2a--WELLID,NNODES'
107   FORMAT(A,I10,A)
C  Item 2b
      IF(IHLIM2(N).EQ.0) THEN
        WRITE(IU,109) LOSNAM(LOSTYP2(N)),
     1           '    0','    0','    0','    0',
     2      '          2b--LOSSTYPE,PUMPLOC,Qlimit,PPFLAG,PUMPCAP'
109     FORMAT(5X,A,4A,A)
      ELSE
        WRITE(IU,110) LOSNAM(LOSTYP2(N)),
     1           '    0','   -1','    0','    0',
     2      '          2b--LOSSTYPE,PUMPLOC,Qlimit,PPFLAG,PUMPCAP'
110     FORMAT(5X,A,4A,A)
      END IF
C  Item 2c
      IF(LOSTYP2(N).EQ.0) THEN
      ELSE IF(LOSTYP2(N).EQ.1) THEN
        WRITE(IU,111) '   -1','               2c(THIEM)--RW'
111     FORMAT(A,25X,A)
      ELSE IF(LOSTYP2(N).EQ.2) THEN
        WRITE(IU,113) '   -1   -1   -1',
     1           '               2c(SKIN)--RW,Rskin,Kskin'
113     FORMAT(A,15X,A)
      ELSE IF(LOSTYP2(N).EQ.3) THEN
        WRITE(IU,115) '   -1   -1   -1   -1',
     1          '          2c(GENERAL)--RW,B,C,P'
115     FORMAT(A,15X,A)
      ELSE IF(LOSTYP2(N).EQ.4) THEN
        WRITE(IU,117) '   -1','               2c(SpecifyCWC)--CWC'
117     FORMAT(A,25X,A)
      END IF
C  Item 2d -- for each node in the well
      DO 50 NN=1,IL2(MXLAY+1,N)
      IF(LOSTYP2(N).EQ.0) THEN
C  None
        WRITE(IU,*) IL2(NN,N),IR2(NN,N),IC2(NN,N),
     1  '                                      2d(NONE)--LAY,ROW,COL'
      ELSE IF(LOSTYP2(N).EQ.1) THEN
C  Thiem
        WRITE(IU,*) IL2(NN,N),IR2(NN,N),IC2(NN,N),RW2(NN,N),
     1  '                           2d(THIEM)--LAY,ROW,COL,RW'
      ELSE IF(LOSTYP2(N).EQ.2) THEN
C  Skin
        WRITE(IU,*) IL2(NN,N),IR2(NN,N),IC2(NN,N),
     1              RW2(NN,N),C2(NN,N),B2(NN,N),
     2              '    2d(SKIN)--LAY,ROW,COL,RW,Rskin,Kskin'
      ELSE IF(LOSTYP2(N).EQ.3) THEN
C  General
        WRITE(IU,*) IL2(NN,N),IR2(NN,N),IC2(NN,N),
     1           RW2(NN,N),B2(NN,N),C2(NN,N),PLOSS,
     2              '     2d(GENERAL)--LAY,ROW,COL,RW,B,C,P'
      ELSE IF(LOSTYP2(N).EQ.4) THEN
C  SpecifyCWC
        WRITE(IU,*) IL2(NN,N),IR2(NN,N),IC2(NN,N),-RW2(NN,N),
     1    '                           2d(SpecifyCWC)--LAY,ROW,COL,CWC'
      END IF
50    CONTINUE
100   CONTINUE
C
C  STRESS PERIOD DATA
      DO 200 KPER=1,NPER
C
C  Item 3
      WRITE(IU,101) ITMPPER(KPER),
     1    '              3--ITMP, PERIOD',KPER
101   FORMAT(I10,14X,A,I4)
      IF(ITMPPER(KPER).GT.0) THEN
        DO 150 K=1,ITMPPER(KPER)
C  Item 4a
        WRITE(IU,'(A,1PE14.5,A)') MNW2SITE(IWNUM2(K,KPER))(1:20),
     1              Q2(K,KPER),'    4--WELLID,Qdes'
        IF(IHLIM2(IWNUM2(K,KPER)).EQ.1) THEN
C  Item 4b
          IF(ICUT2(K,KPER).EQ.0) THEN
            WRITE(IU,'(1PE14.5,A)') HLIM2(K,KPER),
     1               '    0        4b--Hlim,QCUT'
          ELSE IF(ICUT2(K,KPER).GT.0) THEN
            WRITE(IU,'(1PE14.5,I5,2E14.5,A)') HLIM2(K,KPER),
     1         ICUT2(K,KPER),QFRCMN2(K,KPER),QFRCMX2(K,KPER),
     2       ' 4b--Hlim,QCUT,Qfrcmn,Qfrcmx'
          ELSE
C  In MNW1, qfrcmx and qfrcmn are percents -- they are fractions in MNW2
            WRITE(IU,'(1PE14.5,I5,2E14.5,A)') HLIM2(K,KPER),
     1         ICUT2(K,KPER),QFRCMN2(K,KPER)*0.01,QFRCMX2(K,KPER)*0.01,
     2       ' 4b--Hlim,QCUT,Qfrcmn,Qfrcmx'
          END IF
        END IF
150     CONTINUE
      END IF
200   CONTINUE
C
      RETURN
      END
      SUBROUTINE NAMGEN(MSTART,MEND,STMP)
      USE GWFMNWMODULE
      CHARACTER*(*) STMP
C
      STMP='W'
      WRITE(STMP(2:7),'(2I3.3)') IC(MSTART),IR(MSTART)
      I1=8
      DO 10 M=MSTART,MEND
      IF(I1.GT.30) THEN
        WRITE(*,*) 'Generated site name > 32 characters'
        STOP
      END IF
      WRITE(STMP(I1:I1+1),'(I2.2)') IL(M)
      I1=I1+2
10    CONTINUE
C
      RETURN
      END
