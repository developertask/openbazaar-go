/* Defines the GLEEC_ARGCHK macro used within the library */
/* ARGTYPE is defined in mycrypt_cfg.h */
#if ARGTYPE == 0

#include <signal.h>

/* this is the default LibTomCrypt macro  */
void crypt_argchk(char *v, char *s, int d);
#define GLEEC_ARGCHK(x) if (!(x)) { crypt_argchk(#x, __FILE__, __LINE__); }
#define GLEEC_ARGCHKVD(x) GLEEC_ARGCHK(x)

#elif ARGTYPE == 1

/* fatal type of error */
#define GLEEC_ARGCHK(x) assert((x))
#define GLEEC_ARGCHKVD(x) GLEEC_ARGCHK(x)

#elif ARGTYPE == 2

#define GLEEC_ARGCHK(x) if (!(x)) { fprintf(stderr, "\nwarning: ARGCHK failed at %s:%d\n", __FILE__, __LINE__); }
#define GLEEC_ARGCHKVD(x) GLEEC_ARGCHK(x)

#elif ARGTYPE == 3

#define GLEEC_ARGCHK(x) 
#define GLEEC_ARGCHKVD(x) GLEEC_ARGCHK(x)

#elif ARGTYPE == 4

#define GLEEC_ARGCHK(x)   if (!(x)) return CRYPT_INVALID_ARG;
#define GLEEC_ARGCHKVD(x) if (!(x)) return;

#endif


/* $Source$ */
/* $Revision$ */
/* $Date$ */
