C     Last change:  ERB  23 Aug 2001    9:26 am
CC
       PROGRAM HYDFMT
CC
C----- Reads unformatted data from the HYDMOD package and writes out
C----- columns as formatted data to selected files by topic. The files
C----- have extensions that represent the type of data they contain.
C----- The three-letter extensions are as follows:
C-----      TYPE OF DATA                                      OUTPUT FILE
C-----                                                          EXTENSION
C----- (1)  ground-water levels (head)                              .gwh
C----- (2)  ground-water level decline (drawdown)                   .gwd
C----- (3)  ground-water preconsolidation level (critical head)     .crh
C----- (4)  layer-specific compaction (compaction)                  .cmp
C----- (5)  sum of all layer compaction (subsidence)                .sub
C----- (6)  surface-water streamflow water level (stage)            .sth
C----- (7)  surface-water streamflow into a reach (inflow)          .inf
C----- (8)  surface-water streamflow out of a reach (inflow)        .otf
C----- (9)  flow between ground-water & surface-water (leakage)     .gsf
C-----
C----- R.T. Hanson, USGS-WRD, San Diego, California, rthanson@usgs.gov
C----- S.A. Leake, USGS-WRD, Tucson, Arizona, saleake@usgs.gov
C-----
C----- VERSION 0100 29JULY1998 HYDFMT
C=============================================================================
      CHARACTER FN1*80,FN2*80,FMT1*80,FN3*80,WELLID*20
      CHARACTER TIMTYP*1,ELPTYP*1,arr*2,timlbl*4,fmtout*27,fmtoute*17
C      character fmtoutd*20,blank*80,SITTYP*1,LEAPYR*1/'L'/
      character fmtoutd*20,blank*80,SITTYP*1,LEAPYR*1
      character WELLIDH*20,WELLIDD*20,WELLIDCH*20,
     & WELLIDC*20,WELLIDS*20,WELLIDFI*20,
     & WELLIDHF*20,WELLIDFO*20,WELLIDFA*20
      DIMENSION JCOL(5000),Z(5000),zh(5000),id(5000),
     & zhd(5000),zhph(5000),zhc(5000),zhs(5000),
     & zfi(5000),zfo(5000),zhf(5000),zfa(5000)
      DOUBLE PRECISION DTIME,DZ(5000)
       DIMENSION WELLID(5000),WELLIDH(5000),WELLIDD(5000),
     & WELLIDCH(5000),
     & WELLIDC(5000),WELLIDS(5000),WELLIDFI(5000),
     & WELLIDHF(5000),WELLIDFO(5000),WELLIDFA(5000)
      INTEGER DAYS,IDATE,nu(9),icnt(9)
      INTEGER ISTRNG
      LOGICAL FIRST,GEN
      DATA FIRST,GEN/.TRUE.,.TRUE./
CC
      COMMON /T/YR,LEAPYR
cc
       DATA (wellid(i),i=1,5000)/5000*' ------------------ '/,
     &(wellidh(i),i=1,5000)/5000*' ------------------ '/,
     &(wellidd(i),i=1,5000)/5000*' ------------------ '/,
     &(wellidch(i),i=1,5000)/5000*' ------------------ '/,
     &(wellidc(i),i=1,5000)/5000*' ------------------ '/,
     &(wellids(i),i=1,5000)/5000*' ------------------ '/,
     &(wellidfi(i),i=1,5000)/5000*' ------------------ '/,
     &(wellidfo(i),i=1,5000)/5000*' ------------------ '/,
     &(wellidfa(i),i=1,5000)/5000*' ------------------ '/,
     &(wellidhf(i),i=1,5000)/5000*' ------------------ '/,
     &(nu(i),i=1,9)/61,62,63,64,65,66,67,68,69/,
     &(icnt(i),i=1,9)/9*0/
cc
       DATA blank/'
     &                           '/
C
      LEAPYR='L'
      inunit=60
      fmt1='                                       '
      fmtout='(i4,1x,a4,12x,5000(1x,a20))'
      fmtoute='(f10.3,5000f21.2)'
      fmtoutd='(1x,i8,3x,5000f21.2)'
      TIMTYP='D'
      ELPTYP='Y'
      NDATE=1
      START=0.0
      numhh=0
      numhd=0
      numch=0
      numhc=0
      numhs=0
      numhfi=0
      numhfo=0
      numhfa=0
      numhhf=0
      LEN=0
      ISTRNG=80
      FN1=blank
      FN2=blank
      FN3=blank
      FMT1=blank
CC
C----- Read file names
    1 WRITE(*,*) 'Enter name of file with unformatted hydrograph data:'
      READ(*,'(A)') FN1
      IF(FN1.EQ.'        ') GO TO 100
      ! Use the following line when compiling with Absoft compiler
      !OPEN(UNIT=inunit,FILE=FN1,FORM='UNFORMATTED',ACCESS='TRANSPARENT')
      ! Use the following line when compiling with Lahey or Intel compiler
      OPEN(UNIT=inunit,FILE=FN1,FORM='BINARY',ACCESS='SEQUENTIAL',
     &        STATUS='OLD')
CC
C----- Read first unformatted header record with number of hydrographs saved.
C----- Negative number indicates double precision
      READ(inunit) NUMH,ITMUNI
      IF(NUMH.LT.0) THEN
        NUMH=-NUMH
        IPREC=2
        WRITE(*,*) 'Double precision hydrograph save file'
      ELSE
        IPREC=1
        WRITE(*,*) 'Single precision hydrograph save file'
      END IF
C----- Read second unformatted header record with labels of hydrographs saved
      READ(inunit) timlbl,(wellid(n)(1:20),n=1,numh)
      WRITE(*,*) 'Enter root-name of file for formatted output',
     &' (ex. hydro):'
      READ(*,'(A)') FN2
      CALL LNOTE(FN2,ISTRNG,LEN)
      if(LEN.gt.76)LEN=76
CC
      WRITE(*,*)'DO YOU WANT DECIMAL OR CALENDAR(DATE) ',
     &'TIME FORMAT(D/C):'
      READ(*,*)TIMTYP
      IF(TIMTYP.EQ.'C'.or.TIMTYP.EQ.'c')THEN
       WRITE(*,*)'ENTER INITIAL DATE OF TRANSIENT SIMULATION ',
     &'(YYYYMMDD ex. 19920827):'
       READ(*,*)ISTRT
       ISTT=(ISTRT/1000000)
       IST=ISTT*1000000
       ISTART=ISTRT-IST
       IDAYS=DAYS(ISTART)
      ELSE IF(TIMTYP.EQ.'D'.or.TIMTYP.EQ.'d')THEN
       WRITE(*,*)'ENTER UNIT DECIMAL TIME AS YEARS, DAYS, OR MINUTES',
     &' (Y,D,M) FOR OUTPUT:'
       READ(*,*)ELPTYP
       WRITE(*,*)'ENTER INITIAL DECIMAL TIME OF TRANSIENT',
     &' SIMULATION (ex. 1891.00):'
       READ(*,*)START
      ENDIF
      WRITE(*,*)'DO YOU IGNORE LEAP DAYS,'
      WRITE(*,*)'DISTRIBUTE THEM UNIFORMLY OVER FOUR YEARS, OR'
      WRITE(*,*)'DO YOU WANT THE LEAP DAY INSERTED INTO THE LEAP YEAR?'
      WRITE(*,*)'ENTER A CHOICE FOR IGNORE, UNIFORM, OR LEAP (I/U/L):'
      READ(*,*)LEAPYR
       if(timtyp.eq.'D'.or.timtyp.eq.'d')then
        FMT1(1:17)=fmtoute
       elseif(timtyp.eq.'C'.or.timtyp.eq.'c')then
        FMT1(1:20)=fmtoutd
       endif
       do 22 ii=1,numh
       CALL LEFTJ(wellid(ii))
          read(wellid(ii)(1:2),'(a2)')arr
       if(arr.eq.'HD')then
        id(ii)=1
        numhh=numhh+1
        wellidh(numhh)=wellid(ii)
       elseif(arr.eq.'DD')then
        id(ii)=2
        numhd=numhd+1
        wellidd(numhd)=wellid(ii)
       elseif(arr.eq.'HC')then
        id(ii)=3
        numch=numch+1
        wellidch(numch)=wellid(ii)
       elseif(arr.eq.'CP')then
        id(ii)=4
        numhc=numhc+1
        wellidc(numhc)=wellid(ii)
       elseif(arr.eq.'SB')then
        id(ii)=5
        numhs=numhs+1
        wellids(numhs)=wellid(ii)
       elseif(arr.eq.'ST')then
        id(ii)=6
        numhhf=numhhf+1
        wellidhf(numhhf)=wellid(ii)
       elseif(arr.eq.'SI')then
        id(ii)=7
        numhfi=numhfi+1
        wellidfi(numhfi)=wellid(ii)
       elseif(arr.eq.'SO')then
        id(ii)=8
        numhfo=numhfo+1
        wellidfo(numhfo)=wellid(ii)
       elseif(arr.eq.'SA')then
        id(ii)=9
        numhfa=numhfa+1
        wellidfa(numhfa)=wellid(ii)
       endif
  22   continue
cc
      if(numhh.gt.0)then
       write(FN2(LEN+1:LEN+4),'(A)')'.gwh'
       OPEN(UNIT=nu(1),FILE=FN2,FORM='FORMATTED',ACCESS='SEQUENTIAL')
       write(nu(1),fmt=fmtout)numhh,timlbl,
     & (wellidh(n)(1:20),n=1,numhh)
      endif
      if(numhd.gt.0)then
       write(FN2(LEN+1:LEN+4),'(A)')'.gwd'
       OPEN(UNIT=nu(2),FILE=FN2,FORM='FORMATTED',ACCESS='SEQUENTIAL')
       write(nu(2),fmt=fmtout)numhd,timlbl,
     & (wellidd(n)(1:20),n=1,numhd)
      endif
      if(numch.gt.0)then
       write(FN2(LEN+1:LEN+4),'(A)')'.crh'
       OPEN(UNIT=nu(3),FILE=FN2,FORM='FORMATTED',ACCESS='SEQUENTIAL')
       write(nu(3),fmt=fmtout)numch,timlbl,
     & (wellidch(n)(1:20),n=1,numch)
      endif
      if(numhc.gt.0)then
       write(FN2(LEN+1:LEN+4),'(A)')'.cmp'
       OPEN(UNIT=nu(4),FILE=FN2,FORM='FORMATTED',ACCESS='SEQUENTIAL')
       write(nu(4),fmt=fmtout)numhc,timlbl,
     & (wellidc(n)(1:20),n=1,numhc)
      endif
      if(numhs.gt.0)then
       write(FN2(LEN+1:LEN+4),'(A)')'.sub'
       OPEN(UNIT=nu(5),FILE=FN2,FORM='FORMATTED',ACCESS='SEQUENTIAL')
       write(nu(5),fmt=fmtout)numhs,timlbl,
     & (wellids(n)(1:20),n=1,numhs)
      endif
      if(numhhf.gt.0)then
       write(FN2(LEN+1:LEN+4),'(A)')'.sth'
       OPEN(UNIT=nu(6),FILE=FN2,FORM='FORMATTED',ACCESS='SEQUENTIAL')
       write(nu(6),fmt=fmtout)numhhf,timlbl,
     & (wellidhf(n)(1:20),n=1,numhhf)
      endif
      if(numhfi.gt.0)then
       write(FN2(LEN+1:LEN+4),'(A)')'.inf'
       OPEN(UNIT=nu(7),FILE=FN2,FORM='FORMATTED',ACCESS='SEQUENTIAL')
       write(nu(7),fmt=fmtout)numhfi,timlbl,
     & (wellidfi(n)(1:20),n=1,numhfi)
      endif
      if(numhfo.gt.0)then
       write(FN2(LEN+1:LEN+4),'(A)')'.otf'
       OPEN(UNIT=nu(8),FILE=FN2,FORM='FORMATTED',ACCESS='SEQUENTIAL')
       write(nu(8),fmt=fmtout)numhfo,timlbl,
     & (wellidfo(n)(1:20),n=1,numhfo)
      endif
      if(numhfa.gt.0)then
       write(FN2(LEN+1:LEN+4),'(A)')'.gsf'
       OPEN(UNIT=nu(9),FILE=FN2,FORM='FORMATTED',ACCESS='SEQUENTIAL')
       write(nu(9),fmt=fmtout)numhfa,timlbl,
     & (wellidfa(n)(1:20),n=1,numhfa)
      endif
cc
C----- Read the number of columns to be written to output file
C----- The number of columns does not include the simulation time which is
C----- always the first column in the formatted file.
      WRITE(*,*)'DO YOU WANT ALL OR SELECTED SITES(A/S):'
      READ(*,*)SITTYP
      IF(SITTYP.EQ.'A'.OR.SITTYP.EQ.'a')then
       GEN=.TRUE.
       NC=numh
       DO 21 IK=1,numh
  21    JCOL(IK)=IK
      ELSEIF(SITTYP.EQ.'S'.OR.SITTYP.EQ.'s')then
   5   WRITE(*,*) 'Enter number of columns to be read:'
       READ(*,*) NC
       WRITE(*,10) NC
       GEN=.FALSE.
C----- Read the column numbers, free format, any order
   10  FORMAT('Enter ',I3,' column numbers:')
       READ(*,*) (JCOL(N),N=1,NC)
C----- Read format for output of data, free format, no quotes.  Example:
C-----      (F10.2,4F10.3)
C----- This example writes simulation time with F10.3 and thirty columns of
C----- observations with F10.2
       WRITE(*,*)'Enter format for output (ex (F10.3,30F10.2) or (*):'
       READ(*,'(A)') FMT1
      DO 25 N=1,NC
      IF(JCOL(N).GT.NUMH) THEN
       WRITE(*,20) JCOL(N),NUMH
   20  FORMAT(' Column number',I3,' is greater than maximum possible of'
     1         ,I3,/,' please reenter column numbers...')
       GO TO 5
      ENDIF
   25 CONTINUE
      ENDIF
C----- Read the unformatted and Write the formatted results
   30 IF(IPREC.EQ.1) THEN
C        READ(inunit,ERR=50) TIME,(Z(N),N=1,NUMH) ! Use when access=transparent
        READ(inunit,END=50) TIME,(Z(N),N=1,NUMH)
      ELSE
C        READ(inunit,ERR=50) DTIME,(DZ(N),N=1,NUMH) ! Use when access=transparent
        READ(inunit,END=50) DTIME,(DZ(N),N=1,NUMH)
        TIME=DTIME
        DO 31 N=1,NUMH
        Z(N)=DZ(N)
   31   CONTINUE
      END IF
C----- Convert model elapsed time into calendar time
      CALL MODTIME(ITIME,TIME,ITMUNI,IDAYS,IDATE,ISTART,TIMTYP,
     -ELPTYP,FIRST,START)
      FIRST=.FALSE.
      IF(TIMTYP.EQ.'C'.or.TIMTYP.EQ.'c')IDATE=IDATE+IST
cc
       do 89 ii=1,NC
       if(id(ii).gt.0)icnt(id(ii))=icnt(id(ii))+1
       if(id(ii).eq.1)then
        zh(icnt(id(ii)))=Z(JCOL(ii))
       elseif(id(ii).eq.2)then
        zhd(icnt(id(ii)))=Z(JCOL(ii))
       elseif(id(ii).eq.3)then
        zhph(icnt(id(ii)))=Z(JCOL(ii))
       elseif(id(ii).eq.4)then
        zhc(icnt(id(ii)))=Z(JCOL(ii))
       elseif(id(ii).eq.5)then
        zhs(icnt(id(ii)))=Z(JCOL(ii))
       elseif(id(ii).eq.6)then
        zhf(icnt(id(ii)))=Z(JCOL(ii))
       elseif(id(ii).eq.7)then
        zfi(icnt(id(ii)))=Z(JCOL(ii))
       elseif(id(ii).eq.8)then
        zfo(icnt(id(ii)))=Z(JCOL(ii))
       elseif(id(ii).eq.9)then
        zfa(icnt(id(ii)))=Z(JCOL(ii))
       endif
   89  continue
cc
      IF(FMT1(1:3).EQ.'(*)')THEN
       IYEAR=IDATE/10000
       IMON=(IDATE-(IYEAR*10000))/100
       IDAY=(IDATE-(IYEAR*10000)-(IMON*100))
       IF(IYEAR.LE.99)IYEAR=1900+IYEAR
       IF(IDATE.LT.ISTART)IYEAR=2000+IYEAR
       IDATE=IMON*1000000+IDAY*10000+IYEAR
      if(numhh.gt.0)then
       DO 91 N=1,numhh
 91    WRITE(nu(1),*)WELLIDH(N),',',IDATE,',',ZH(N)
      endif
      if(numhd.gt.0)then
       DO 92 N=1,numhd
 92    WRITE(nu(2),*)WELLIDD(N),',',IDATE,',',ZHD(N)
      endif
      if(numch.gt.0)then
       DO 93 N=1,numch
 93    WRITE(nu(3),*)WELLIDCH(N),',',IDATE,',',ZHPH(N)
      endif
      if(numhc.gt.0)then
       DO 94 N=1,numhc
 94    WRITE(nu(4),*)WELLIDC(N),',',IDATE,',',ZHC(N)
      endif
      if(numhs.gt.0)then
       DO 95 N=1,numhs
 95    WRITE(nu(4),*)WELLIDS(N),',',IDATE,',',ZHS(N)
      endif
      if(numhhf.gt.0)then
       DO 96 N=1,numhhf
 96    WRITE(nu(6),*)WELLIDHF(N),',',IDATE,',',ZHF(N)
      endif
      if(numhfi.gt.0)then
       DO 97 N=1,numhfi
 97    WRITE(nu(7),*)WELLIDFI(N),',',IDATE,',',ZFI(N)
      endif
      if(numhfo.gt.0)then
       DO 98 N=1,numhfo
 98    WRITE(nu(8),*)WELLIDFO(N),',',IDATE,',',ZFO(N)
      endif
      if(numhfa.gt.0)then
       DO 99 N=1,numhfa
 99    WRITE(nu(9),*)WELLIDFA(N),',',IDATE,',',ZFA(N)
      endif
      ELSE IF (FMT1(1:3).NE.'(*)'.and.(TIMTYP.EQ.'C'.or.
     &TIMTYP.EQ.'c'))THEN
       if(numhh.gt.0)WRITE(nu(1),FMT1) IDATE,(ZH(N),N=1,numhh)
       if(numhd.gt.0)WRITE(nu(2),FMT1) IDATE,(ZHD(N),N=1,numhd)
       if(numch.gt.0)WRITE(nu(3),FMT1) IDATE,(ZHPH(N),N=1,numch)
       if(numhc.gt.0)WRITE(nu(4),FMT1) IDATE,(ZHC(N),N=1,numhc)
       if(numhs.gt.0)WRITE(nu(5),FMT1) IDATE,(ZHS(N),N=1,numhs)
       if(numhhf.gt.0)WRITE(nu(6),FMT1) IDATE,(ZHF(N),N=1,numhhf)
       if(numhfi.gt.0)WRITE(nu(7),FMT1) IDATE,(ZFI(N),N=1,numhfi)
       if(numhfo.gt.0)WRITE(nu(8),FMT1) IDATE,(ZFO(N),N=1,numhfo)
       if(numhfa.gt.0)WRITE(nu(9),FMT1) IDATE,(ZFA(N),N=1,numhfa)
      ELSE IF (FMT1(1:3).NE.'(*)'.and.(TIMTYP.EQ.'D'.or.
     &TIMTYP.EQ.'d'))THEN
       if(numhh.gt.0)WRITE(nu(1),FMT1) TIME,(ZH(N),N=1,numhh)
       if(numhd.gt.0)WRITE(nu(2),FMT1) TIME,(ZHD(N),N=1,numhd)
       if(numch.gt.0)WRITE(nu(3),FMT1) TIME,(ZHPH(N),N=1,numch)
       if(numhc.gt.0)WRITE(nu(4),FMT1) TIME,(ZHC(N),N=1,numhc)
       if(numhs.gt.0)WRITE(nu(5),FMT1) TIME,(ZHS(N),N=1,numhs)
       if(numhhf.gt.0)WRITE(nu(6),FMT1) TIME,(ZHF(N),N=1,numhhf)
       if(numhfi.gt.0)WRITE(nu(7),FMT1) TIME,(ZFI(N),N=1,numhfi)
       if(numhfo.gt.0)WRITE(nu(8),FMT1) TIME,(ZFO(N),N=1,numhfo)
       if(numhfa.gt.0)WRITE(nu(9),FMT1) TIME,(ZFA(N),N=1,numhfa)
      ENDIF
      do 51 ix=1,9
   51 icnt(ix)=0
      GO TO 30
   50 CLOSE(inunit)
      if(numhh.gt.0)CLOSE(nu(1))
      if(numhd.gt.0)CLOSE(nu(2))
      if(numch.gt.0)CLOSE(nu(3))
      if(numhc.gt.0)CLOSE(nu(4))
      if(numhs.gt.0)CLOSE(nu(5))
      if(numhhf.gt.0)CLOSE(nu(6))
      if(numhfi.gt.0)CLOSE(nu(7))
      if(numhfo.gt.0)CLOSE(nu(8))
      if(numhfa.gt.0)CLOSE(nu(9))
  100 STOP
      END
C*******************************************************************************
      SUBROUTINE MODTIME(ITIME,TOTIM,ITMUNI,IDAYS,IDATE,ISTART,
     -TIMTYP,ELPTYP,FIRST,START)
CC
C-----
C----- VERSION 0100 29JULY1998 MODTIME
C     ***********************************************************************
C     CONVERT ELAPSED MODEL TIME TO DECIMAL OR CLAENDAR DATES FOR HYDROGRAPHS
C     ***********************************************************************
C
C     SPECIFICATIONS:
C     ------------------------------------------------------------------
      CHARACTER TIMTYP*1,ELPTYP*1,LEAPYR*1
      INTEGER DATE1,DAYS
      LOGICAL FIRST
CC
      COMMON /T/YR,LEAPYR
CC

      FYY=0.
      IYY=0
      IF(FIRST)REMTIM=0.0
      IF(LEAPYR.EQ.'U')THEN
       YR=365.25
      ELSE
       YR=365.
      ENDIF
CC
      IF(ITMUNI.EQ.0)THEN
      WRITE(*,*)'TIME UNIT OF MODEL DATA IS UNDEFINED CHECK',
     -'BASIC PACKAGE DATA-->ITMUNI'
      STOP
      ENDIF
CC
CC    SET MULTIPLIER BASED ON MODEL TIME, FOR DATE FORMAT CONVERSION
CC        TO ELAPSED DAYS
CC
      IF(TIMTYP.EQ.'C'.or.TIMTYP.EQ.'c')THEN
       IF(ITMUNI.EQ.1)THEN
        DELTIM=86400.
       ELSE IF(ITMUNI.EQ.2)THEN
        DELTIM=1440.
       ELSE IF(ITMUNI.EQ.3)THEN
        DELTIM=24.
       ELSE IF(ITMUNI.EQ.4)THEN
        DELTIM=1.
       ELSE IF(ITMUNI.EQ.5)THEN
        DELTIM=1./YR
       ENDIF
       ITIME=TOTIM/DELTIM
       REMTIM=(TOTIM/DELTIM)-INT(TOTIM/DELTIM)+REMTIM
       IF((REMTIM-1.).GT.0.)THEN
        REMTIM=REMTIM-1.
        ITIME=ITIME+1
       ENDIF
       ITIME=ITIME+IDAYS
       ITIME2=ITIME
       IDATE=DATE1(ITIME)
       IF(ITMUNI.LT.5)THEN
        YY=(IDATE/10000)-(ISTART/10000)
        IF(LEAPYR.EQ.'L')THEN
         IF((MOD(YY,4.).EQ.0..AND.MOD(YY,100.).NE.0.).OR.
     &       (MOD(YY,400.).EQ.0.))THEN
           ITIME2=ITIME2+INT(YY/4.)+1
         ELSEIF(MOD(YY,4.).NE.0.)THEN
           ITIME2=ITIME2+INT(YY/4.)
         ENDIF
        ENDIF
        IDATE=DATE1(ITIME2)
       ENDIF
CC
CC    SET MULTIPLIER BASED ON MODEL TIME FOR DECIMAL TIME FLAG ELPTYP
CC
      ELSE IF(TIMTYP.EQ.'D'.or.TIMTYP.EQ.'d')THEN
       IF(ELPTYP.EQ.'M'.or.ELPTYP.EQ.'m')THEN
        IF(ITMUNI.EQ.1)THEN
         DELTIM=60.
        ELSE IF(ITMUNI.EQ.2)THEN
         DELTIM=1.
        ELSE IF(ITMUNI.EQ.3)THEN
         DELTIM=1/60.
        ELSE IF(ITMUNI.EQ.4)THEN
         DELTIM=1/1440.
        ELSE IF(ITMUNI.EQ.5)THEN
         DELTIM=1./525600.
        ENDIF
       ELSE IF(ELPTYP.EQ.'D'.or.ELPTYP.EQ.'d')THEN
        IF(ITMUNI.EQ.1)THEN
         DELTIM=86400.
        ELSE IF(ITMUNI.EQ.2)THEN
         DELTIM=1440.
        ELSE IF(ITMUNI.EQ.3)THEN
         DELTIM=24.
        ELSE IF(ITMUNI.EQ.4)THEN
         DELTIM=1.
        ELSE IF(ITMUNI.EQ.5)THEN
         DELTIM=1./YR
        ENDIF
       ELSE IF(ELPTYP.EQ.'Y'.or.ELPTYP.EQ.'y')THEN
        IF(ITMUNI.EQ.1)THEN
         DELTIM=31536000.
        ELSE IF(ITMUNI.EQ.2)THEN
         DELTIM=525600.
        ELSE IF(ITMUNI.EQ.3)THEN
         DELTIM=8760.
        ELSE IF(ITMUNI.EQ.4)THEN
         DELTIM=YR
        ELSE IF(ITMUNI.EQ.5)THEN
         DELTIM=1.
        ENDIF
       TOTIM=(TOTIM/DELTIM)+START
       GOTO 99
       ENDIF
      ISTY=(ISTART/10000)*10000
      IYY=DAYS(ISTART)-DAYS(ISTY)-1
      FYY=FLOAT(IYY)/YR
      YY=START+(ISTART/10000)+FYY
      TOTIM=TOTIM/DELTIM
      ENDIF
  99  RETURN
      END
C
C*******************************************************************************
CC
      INTEGER FUNCTION DAYS(DAT)
C-----
C----- VERSION 0100 29JULY1998 DAYS
C     ***********************************************************************
CC     FOR DATE GIVEN AS AN INTEGER YYMMDD, THIS FUNCTION RETURNS
CC     THE NUMBER OF DAYS SINCE DECEMBER 31, 1899.
C     ***********************************************************************
C
C     SPECIFICATIONS:
C     ------------------------------------------------------------------
CC
      INTEGER DAT,YEAR,DAY,DAYM(12)
      CHARACTER*1 LEAPYR
CC
      COMMON /T/YR,LEAPYR
CC
      DATA DAYM/0,31,59,90,120,151,181,212,243,273,304,334/
CC
      YEAR=DAT/10000
      M=DAT-YEAR*10000
      MONTH=M/100
      DAY=M-MONTH*100
      IF(MONTH.LT.1)MONTH=1
      IF(DAY.LT.1)DAY=1
      IF(LEAPYR.EQ.'U')THEN
       YR=365.25
       DAYS=YEAR*YR
      ELSEIF(LEAPYR.EQ.'L')THEN
       YR=365.
       DAYS=YEAR*YR+(YEAR+3)/4
      ELSE
       YR=365.
       DAYS=YEAR*YR
      ENDIF
      DAYS=DAYS+DAYM(MONTH)+DAY
      IF(MONTH.LE.2)RETURN
      IF(MOD(YEAR,4).NE.0) RETURN
      IF(LEAPYR.EQ.'L')DAYS=DAYS+1
      RETURN
      END
C*******************************************************************************
      INTEGER FUNCTION DATE1(DAYS)
C-----
C----- VERSION 0100 29JULY1998 DATE1
C     ***********************************************************************
CC     FOR VALUE OF DAYS SINCE DECEMBER 31, 1899 FUNCTION RETURNS THE
CC     DATE AS AN INTEGER IN THE FORM YYMMDD
C     ***********************************************************************
C
C     SPECIFICATIONS:
C     ------------------------------------------------------------------
      INTEGER DAYS,DAYM(12,2),YY,MM,DD,DY,NL
CC
      DATA ((DAYM(I,J),I=1,12),J=1,2)
     &/0,31,59,90,120,151,181,212,243,273,304,334,
     & 0,31,60,91,121,152,182,213,244,274,305,335/
CC
      L=1
      NL=0
      IF(DAYS.GE.61) NL=(DAYS-61)/1461+1
      YY=(DAYS-NL-1)/365
      IF(MOD(YY,4).EQ.0) L=2
      DY=DAYS-365*YY-YY/4-(2-L)
      MM=0
   10 MM=MM+1
      IF(MM.EQ.12) GO TO 20
      IF(DY.GT.DAYM(MM+1,L)) GO TO 10
   20 DD=DY-DAYM(MM,L)
      DATE1=10000*YY+100*MM+DD
      RETURN
      END
CC*****************************************************************************
       SUBROUTINE LNOTE(STRING,DIMS,LEN)
C-----
C----- VERSION 0100 29JULY1998 LNOTE
C     ***********************************************************************
CC     RETURNS THE LEFT-JUSTIFIED, NONBLANK LENGTH
CC     FOR A CHARACTER STRING
C     ***********************************************************************
C
C     SPECIFICATIONS:
C     ------------------------------------------------------------------
       INTEGER DIMS,LEN
       CHARACTER STRING*80
       DO 10 N=DIMS,1,-1
       IF(STRING(N:N).NE.' ')GO TO 20
   10  CONTINUE
       LEN=0
       RETURN
   20  LEN=N
       RETURN
       END
CC*****************************************************************************
      SUBROUTINE LEFTJ(STRING)
C-----
C----- VERSION 0100 29JULY1998 LEFTJ
C     ***********************************************************************
CC     RETURNS THE LEFT-JUSTIFIED, NONBLANK
CC     PORTION OF A CHARACTER STRING
C     ***********************************************************************
C
C     SPECIFICATIONS:
C     ------------------------------------------------------------------
      CHARACTER STRING*20
      DO 10 I=1,20
      IF(STRING(I:I).NE.' ') GO TO 20
   10 CONTINUE
      RETURN
   20 STRING=STRING(I:20)
      RETURN
      END
