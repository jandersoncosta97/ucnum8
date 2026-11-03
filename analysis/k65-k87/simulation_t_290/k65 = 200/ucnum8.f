      program ucnum8
c
c     Numerical solution of rate equations for upconversion
c     with 8-level system
c
      implicit none
      integer
     $     maxstp,nmax,nvar,nok,noktot,nbad,nbadtot,kount,
     $     iunit,junit,lunit,munit,
     $     k, i, j, ii, jj, ll, mm, nn, nm, nl, skip, kwrite
      double precision
     $     rate,ystart,ratemax,hmin,h1,tfinal,y,dydx,yscal,eps,x1,x2,
     $     ytemp,ysav,dysav,ytemp1,dytemp1,dytemp2,
     $     zero,one,ten
      character*1 str1
      character*2 str2
      character*4 file1
      character*5 file2
      parameter
     $     (maxstp=10000, nmax=10, eps=1.0d-7)
      dimension
     $     rate(nmax,nmax), ystart(nmax),
     $     y(nmax), dydx(nmax), yscal(nmax),
     $     ytemp(nmax), ysav(nmax), dysav(nmax),
     $     ytemp1(nmax), dytemp1(nmax), dytemp2(nmax)
      data
     $     zero/0.0d0/, one/1.0d0/, ten/1.0d01/
c     
      open(unit=9,file='ET.INP',status='old')
      open(unit=8,file='ET.OUT',status='replace')
      rewind (9,err=1000)
c     
c     read the number of equations (nvar), the final time tfinal
c     (in seconds), and the number of points at which the
c     equations will be integrated.
      read(9,*)
      read(9,*)nvar, tfinal, skip
c
c     nvar = number of states; tfinal = final time;
c     skip = number of calls that will be skipped for printing
c
c     check for the maximum number of equations allowed
      if(nvar .gt. nmax) goto 1002
c     
c     read the initial populations: y(1) y(2) y(3) ... y(nvar)
c     which in general have y(i)=1.0 and y(j.ne.i)=0.0
c     
      do 5 k=1,nvar
         read(9,*) ystart(k)
 5    continue
c     
c     read each transfer rate (in second**-1) in the following
c     order: rate(1,1) rate(1,2) rate(1,3) ... rate(1,n)
c            rate(2,1) rate(2,2) rate(2,3) ... rate(2,n)
c            rate(3,1) rate(3,2) rate(3,3) ... rate(3,n)
c                          ...
c            rate(n,1) rate(n,2) rate(n,3) ... rate(n,n)
c
c     where n=nvar
c     
      ratemax = zero
      do 10 i=1,nvar
         do 11 j=1,nvar
            read(9,*) rate(i,j)
            if(rate(i,j) .gt. ratemax) ratemax = rate(i,j)
 11      continue
 10   continue
c     
      close(unit=9,status='keep')
c     
c     open the units and files for writing the results
      do 15 ii=1,nvar
         iunit=9+ii
         if(ii .lt. 10) then
            write(str1,1060)ii
            file1='pop'//str1
            open(unit=iunit,file=file1,status='replace')
         else
            write(str2,1070)ii
            file2='pop'//str2
            open(unit=iunit,file=file2,status='replace')
         endif
 15   continue
c     
c     write up the initial values
      do 20 jj=1,nvar
         junit=9+jj
         write(junit,1020) x1, ystart(jj)
 20   continue
c     
c     Guess for the initial step (h1)
      h1 = one/(ratemax*ten)
      x1 = zero
      hmin = zero
      kount = 0
      kwrite = skip
      nbadtot = 0
      noktot = 0
 100  continue
      x2 = x1 + h1
      call odeint(ystart,rate,x1,x2,eps,h1,hmin,y,dydx,yscal,
     *            ytemp,ysav,dysav,ytemp1,dytemp1,dytemp2,
     *            nvar,nmax,nok,nbad,maxstp)
c     
      noktot = noktot + nok
      nbadtot = nbadtot + nbad
      kount = kount + 1
c     
c     write up the initial results
      if (kount .eq. 1) then
         do 40 ll=1,nvar
            lunit=9+ll
            write(lunit,1020) x2, ystart(ll)
 40      continue
      endif
c     
c     write up the results after skip times
      if (kount .eq. kwrite) then
         do 45 ll=1,nvar
            lunit=9+ll
            write(lunit,1020) x2, ystart(ll)
 45      continue
         kwrite = kwrite + skip
      endif
c     
      x1 = x2
      if(x2 .lt. tfinal) goto 100
c     
c     close all open units
      do 50 mm=1,nvar
         munit=9+mm
         close(munit,status='keep')
 50   continue
c     
      write(8,*)'Initial Time Step = ', h1
      write(8,*)'Final Time (s) = ', x2
      write(8,*)'Final Populations'
c
      do 60 nn=1,nvar
         write(8,*) ystart(nn)
 60   continue
c
      write(8,*)'Sum of the populations of the donor = ', y(1)+y(2)
      write(8,*)'Sum of the populations of the acceptor = ',
     $     y(3)+y(4)+y(5)+y(6)+y(7)+y(8)
      write(8,*)'Sum of all populations = ',
     $     y(1)+y(2)+y(3)+y(4)+y(5)+y(6)+y(7)+y(8)
c
      write(8,*)'Transition rates (s-1)'
c
      do 70 nm=1,nvar
         do 71 nl=1,nvar
            write(8,*) nm, nl, rate(nm,nl)
 71      continue
 70   continue
c     
      write(8,*)'Normal Termination of UCNUM8'
c
      close(unit=8,status='keep')
c     ! Consider modifying the status of 'keep' above
      stop
c--------------------------------------------------------------------
c    Error messages
c--------------------------------------------------------------------
 1000 write(8,1001)
      stop
 1001 format(10x,'NO INPUT DECK SUPPLIED')
c
 1002 write(8,1003)nmax
      stop
 1003 format(10x,'The maximum number of equations is ',i4)
c
c--------------------------------------------------------------------
c    Formats
c--------------------------------------------------------------------
 1020 format(3x,d15.7,d15.7)
 1030 format(3x,a13,F4.1,a1)
 1060 format(i1)
 1070 format(i2)
      end
c
c
      subroutine odeint(ystart,rate,x1,x2,eps,h1,hmin,y,dydx,yscal,
     $                  ytemp,ysav,dysav,ytemp1,dytemp1,dytemp2,
     $                  nvar,nmax,nok,nbad,maxstp)
      implicit none
      integer
     $     nvar, nmax, nok, nbad, maxstp, nstp, i, j, k 
      double precision
     $     ystart(nmax), rate(nmax,nmax),
     $     y(nmax), dydx(nmax), yscal(nmax),
     $     ytemp(nmax), ysav(nmax), dysav(nmax),
     $     ytemp1(nmax), dytemp1(nmax), dytemp2(nmax),
     $     x1, x2, eps, h1, hmin, tiny, x, h, hdid, hnext,
     $     zero, one
      parameter
     $     (tiny=1.0d-30)
      data
     $     zero /0.0d0/, one /1.0d0/
c
      x = x1
      h = sign(h1,x2-x1)
      nok  = 0
      nbad = 0
c
      do 11 i=1,nvar
         y(i) = ystart(i)
 11   continue
c
      do 24 nstp=1,maxstp
         call derivs(y,dydx,rate,nvar,nmax)
         do 12 j=1,nvar
crll            yscal(j)=abs(y(j))+abs(h*dydx(j))+tiny
c     since some y(i)'s starts and goes to zero, this expression for
c     yscal(j) is not going to work. So, yscal(j) are set the the
c     maximum values of y(i)=1.0
c
            yscal(j) = one
 12      continue
         if((x+h-x2)*(x+h-x1).gt.zero) h=x2-x
c
         call rkqc(y,dydx,rate,yscal,ytemp,ysav,dysav,
     *             ytemp1,dytemp1,dytemp2,
     *             x,h,eps,hdid,hnext,nvar,nmax)
         if (hdid .eq. h)then
            nok = nok + 1
         else
            nbad = nbad + 1
         endif
c
         if ((x-x2)*(x2-x1) .ge. zero)then
c     
            do 14 k=1,nvar
               ystart(k) = y(k)
 14         continue
c     
            h1 = hnext
            return
         endif
c
         if (abs(hnext) .lt. hmin) stop 'Stepsize smaller than minimum'
         h=hnext
c
 24      continue
c
      stop 'Too many steps.'
      end
c
c
      subroutine rkqc(y,dydx,rate,yscal,ytemp,ysav,dysav,
     $                ytemp1,dytemp1,dytemp2,
     $                x,htry,eps,hdid,hnext,n,nmax)
      implicit none
      integer
     $     n, nmax, i, j, k
      double precision
     $     y(nmax),dydx(nmax),rate(nmax,nmax),yscal(nmax),
     $     x,htry,eps,hdid,hnext,
     $     ytemp(nmax),ysav(nmax),dysav(nmax),xsav,h,hh,
     $     ytemp1(nmax),dytemp1(nmax),dytemp2(nmax),
     $     fcor,safety,errcon,pgrow,pshrnk,errmax,
     $     zero,one,half,four 
      parameter
     $     (fcor=0.0666666667d0,safety=0.9d0,errcon=6.0d-4)
      data
     $     zero/0.0d0/, one/1.0d0/, half/0.5d0/, four/4.0d0/
c
      pgrow=-0.20
      pshrnk=-0.25
      xsav=x
c
      do 11 i=1,n
         ysav(i)=y(i)
         dysav(i)=dydx(i)
 11   continue
c
      h=htry
  1   hh=h*half
      call rk4(ysav,dysav,rate,xsav,hh,ytemp,ytemp1,dytemp1,dytemp2,
     *         n,nmax)
      x=xsav+hh
      call derivs(ytemp,dydx,rate,n,nmax)
      call rk4(ytemp,dydx,rate,x,hh,y,ytemp1,dytemp1,dytemp2,
     *         n,nmax)
      x=xsav+h
      if (x. eq. xsav) stop 'Stepsize not significant in rkqc.'
      call rk4(ysav,dysav,rate,xsav,h,ytemp,ytemp1,dytemp1,dytemp2,
     *         n,nmax)
      errmax=zero
      do 12 j=1,n
         ytemp(j)=y(j)-ytemp(j)
         errmax=max(errmax,abs(ytemp(j)/yscal(j)))
 12   continue
      errmax=errmax/eps
      if(errmax.gt.one) then
        h=safety*h*(errmax**pshrnk)
        goto 1
      else
        hdid=h
        if(errmax.gt.errcon)then
          hnext=safety*h*(errmax**pgrow)
        else
          hnext=h*four
        endif
      endif
      do 13 k=1,n
         y(k)=y(k)+ytemp(k)*fcor
 13   continue
      return
      end
c
c
      subroutine rk4(y,dydx,rate,x,h,yout,yt,dyt,dym,n,nmax)
      implicit none
      integer
     $     n, nmax, i, j, k, l
      double precision
     $     y(nmax),dydx(nmax),rate(nmax,nmax),x,h,yout(nmax),
     $     yt(nmax),dyt(nmax),dym(nmax),
     $     hh, h6, xh,
     $     half, two, six
      data
     $     half /0.5d0/, two /2.0d0/, six /6.0d0/
c
      hh=h*half
      h6=h/six
      xh=x+hh
c
      do 11 i=1,n
         yt(i)=y(i)+hh*dydx(i)
 11   continue
      call derivs(yt,dyt,rate,n,nmax)
c
      do 12 j=1,n
         yt(j)=y(j)+hh*dyt(j)
 12   continue
      call derivs(yt,dym,rate,n,nmax)
c
      do 13 k=1,n
         yt(k)=y(k)+h*dym(k)
         dym(k)=dyt(k)+dym(k)
 13   continue
      call derivs(yt,dyt,rate,n,nmax)
c
      do 14 l=1,n
         yout(l)=y(l)+h6*(dydx(l)+dyt(l)+two*dym(l))
 14   continue
c
      return
      end
c
c
      subroutine derivs(y,dydx,k,nvar,nmax)
      implicit none
      integer
     $     nvar, nmax,
     $     i, j
      double precision
     $     y(nmax), dydx(nmax), k(nmax,nmax),
     $     sum, zero
      data zero /0.0d0/
c                                                                    
c     rate equations for 8-level system upconversion       
c                                                                                     
      dydx(1)=-(k(1,2)*y(1)+k(4,2)*y(1)*y(4)+k(8,2)*y(1)*y(8))
     $     +(k(2,1)*y(2)+k(2,4)*y(2)*y(3)+k(2,8)*y(2)*y(4))
      dydx(2)=-(k(2,1)*y(2)+k(2,4)*y(2)*y(3)+k(2,8)*y(2)*y(4))
     $     +(k(1,2)*y(1)+k(4,2)*y(1)*y(4)+k(8,2)*y(1)*y(8))
      dydx(3)=-(k(2,4)*y(2)*y(3))
     $     +(k(4,3)*y(4)+k(5,3)*y(5)+k(6,3)*y(6)+k(7,3)*y(7)
     $     +k(4,2)*y(1)*y(4))
      dydx(4)=-(k(4,3)*y(4)+k(4,2)*y(1)*y(4)+k(2,8)*y(2)*y(4))
     $     +(k(2,4)*y(2)*y(3)+k(8,2)*y(1)*y(8)+k(5,4)*y(5))
      dydx(5)=-(k(5,3)*y(5)+k(5,4)*y(5))
     $     +(k(6,5)*y(6))
      dydx(6)=-(k(6,3)*y(6)+k(6,5)*y(6)+k(6,7)*y(6))
     $     +(k(7,6)*y(7))
      dydx(7)=-(k(7,3)*y(7)+k(7,6)*y(7))
     $     +(k(6,7)*y(6)+k(8,7)*y(8))
      dydx(8)=-(k(8,7)*y(8)+k(8,2)*y(8)*y(1))
     $     +(k(2,8)*y(2)*y(4))
c      
      return
      end
c
