#ifndef TOMCRYPT_CUSTOM_H_
#define TOMCRYPT_CUSTOM_H_

/* macros for various libc functions you can change for embedded targets */
#ifndef XMALLOC
   #ifdef malloc 
   #define GLEEC_NO_PROTOTYPES
   #endif
#define XMALLOC  malloc
#endif
#ifndef XREALLOC
   #ifdef realloc 
   #define GLEEC_NO_PROTOTYPES
   #endif
#define XREALLOC realloc
#endif
#ifndef XCALLOC
   #ifdef calloc 
   #define GLEEC_NO_PROTOTYPES
   #endif
#define XCALLOC  calloc
#endif
#ifndef XFREE
   #ifdef free
   #define GLEEC_NO_PROTOTYPES
   #endif
#define XFREE    free
#endif

#ifndef XMEMSET
   #ifdef memset
   #define GLEEC_NO_PROTOTYPES
   #endif
#define XMEMSET  memset
#endif
#ifndef XMEMCPY
   #ifdef memcpy
   #define GLEEC_NO_PROTOTYPES
   #endif
#define XMEMCPY  memcpy
#endif
#ifndef XMEMCMP
   #ifdef memcmp 
   #define GLEEC_NO_PROTOTYPES
   #endif
#define XMEMCMP  memcmp
#endif
#ifndef XSTRCMP
   #ifdef strcmp
   #define GLEEC_NO_PROTOTYPES
   #endif
#define XSTRCMP strcmp
#endif

#ifndef XCLOCK
#define XCLOCK   clock
#endif
#ifndef XCLOCKS_PER_SEC
#define XCLOCKS_PER_SEC CLOCKS_PER_SEC
#endif

#ifndef XQSORT
   #ifdef qsort
   #define GLEEC_NO_PROTOTYPES
   #endif
#define XQSORT qsort
#endif

/* Easy button? */
#ifdef GLEEC_EASY
   #define GLEEC_NO_CIPHERS
   #define GLEEC_RIJNDAEL
   #define GLEEC_BLOWFISH
   #define GLEEC_DES
   #define GLEEC_CAST5
   
   #define GLEEC_NO_MODES
   #define GLEEC_ECB_MODE
   #define GLEEC_CBC_MODE
   #define GLEEC_CTR_MODE
   
   #define GLEEC_NO_HASHES
   #define GLEEC_SHA1
   #define GLEEC_SHA512
   #define GLEEC_SHA384
   #define GLEEC_SHA256
   #define GLEEC_SHA224
   
   #define GLEEC_NO_MACS
   #define GLEEC_HMAC
   #define GLEEC_OMAC
   #define GLEEC_CCM_MODE

   #define GLEEC_NO_PRNGS
   #define GLEEC_SPRNG
   #define GLEEC_YARROW
   #define GLEEC_DEVRANDOM
   #define TRY_URANDOM_FIRST
      
   #define GLEEC_NO_PK
   #define GLEEC_MRSA
   #define GLEEC_MECC
#endif   

/* Use small code where possible */
/* #define GLEEC_SMALL_CODE */

/* Enable self-test test vector checking */
#ifndef GLEEC_NO_TEST
   #define GLEEC_TEST
#endif

/* clean the stack of functions which put private information on stack */
#define GLEEC_CLEAN_STACK

/* disable all file related functions */
/* #define GLEEC_NO_FILE */

/* disable all forms of ASM */
/* #define GLEEC_NO_ASM */

/* disable FAST mode */
/* #define GLEEC_NO_FAST */

/* disable BSWAP on x86 */
/* #define GLEEC_NO_BSWAP */

/* ---> Symmetric Block Ciphers <--- */
#ifndef GLEEC_NO_CIPHERS

#define GLEEC_BLOWFISH
#define GLEEC_RC2
#define GLEEC_RC5
#define GLEEC_RC6
#define GLEEC_SAFERP
#define GLEEC_RIJNDAEL
#define GLEEC_XTEA
/* _TABLES tells it to use tables during setup, _SMALL means to use the smaller scheduled key format
 * (saves 4KB of ram), _ALL_TABLES enables all tables during setup */
#define GLEEC_TWOFISH
#ifndef GLEEC_NO_TABLES
   #define GLEEC_TWOFISH_TABLES
   /* #define GLEEC_TWOFISH_ALL_TABLES */
#else
   #define GLEEC_TWOFISH_SMALL
#endif
/* #define GLEEC_TWOFISH_SMALL */
/* GLEEC_DES includes EDE triple-GLEEC_DES */
#define GLEEC_DES
#define GLEEC_CAST5
#define GLEEC_NOEKEON
#define GLEEC_SKIPJACK
#define GLEEC_SAFER
#define GLEEC_KHAZAD
#define GLEEC_ANUBIS
#define GLEEC_ANUBIS_TWEAK
#define GLEEC_KSEED
#define GLEEC_KASUMI
#define GLEEC_MULTI2
#define GLEEC_CAMELLIA

#endif /* GLEEC_NO_CIPHERS */


/* ---> Block Cipher Modes of Operation <--- */
#ifndef GLEEC_NO_MODES

#define GLEEC_CFB_MODE
#define GLEEC_OFB_MODE
#define GLEEC_ECB_MODE
#define GLEEC_CBC_MODE
#define GLEEC_CTR_MODE

/* F8 chaining mode */
#define GLEEC_F8_MODE

/* LRW mode */
#define GLEEC_LRW_MODE
#ifndef GLEEC_NO_TABLES
   /* like GCM mode this will enable 16 8x128 tables [64KB] that make
    * seeking very fast.  
    */
   #define LRW_TABLES
#endif

/* XTS mode */
#define GLEEC_XTS_MODE

#endif /* GLEEC_NO_MODES */

/* ---> One-Way Hash Functions <--- */
#ifndef GLEEC_NO_HASHES 

#define GLEEC_CHC_HASH
#define GLEEC_WHIRLPOOL
#define GLEEC_SHA512
#define GLEEC_SHA384
#define GLEEC_SHA256
#define GLEEC_TIGER
#define GLEEC_SHA1
#define GLEEC_MD5
#define GLEEC_MD4
#define GLEEC_MD2
#define GLEEC_RIPEMD128
#define GLEEC_RIPEMD160
#define GLEEC_RIPEMD256
#define GLEEC_RIPEMD320

#endif /* GLEEC_NO_HASHES */

/* ---> MAC functions <--- */
#ifndef GLEEC_NO_MACS

#define GLEEC_HMAC
#define GLEEC_OMAC
#define GLEEC_PMAC
#define GLEEC_XCBC
#define GLEEC_F9_MODE
#define GLEEC_PELICAN

#if defined(GLEEC_PELICAN) && !defined(GLEEC_RIJNDAEL)
   #error Pelican-MAC requires GLEEC_RIJNDAEL
#endif

/* ---> Encrypt + Authenticate Modes <--- */

#define GLEEC_EAX_MODE
#if defined(GLEEC_EAX_MODE) && !(defined(GLEEC_CTR_MODE) && defined(GLEEC_OMAC))
   #error GLEEC_EAX_MODE requires CTR and GLEEC_OMAC mode
#endif

#define GLEEC_OCB_MODE
#define GLEEC_CCM_MODE
#define GLEEC_GCM_MODE

/* Use 64KiB tables */
#ifndef GLEEC_NO_TABLES
   #define GLEEC_GCM_TABLES 
#endif

/* USE SSE2? requires GCC works on x86_32 and x86_64*/
#ifdef GLEEC_GCM_TABLES
/* #define GLEEC_GCM_TABLES_SSE2 */
#endif

#endif /* GLEEC_NO_MACS */

/* Various tidbits of modern neatoness */
#define GLEEC_BASE64

/* --> Pseudo Random Number Generators <--- */
#ifndef GLEEC_NO_PRNGS

/* Yarrow */
#define GLEEC_YARROW
/* which descriptor of AES to use?  */
/* 0 = rijndael_enc 1 = aes_enc, 2 = rijndael [full], 3 = aes [full] */
#define GLEEC_YARROW_AES 0

#if defined(GLEEC_YARROW) && !defined(GLEEC_CTR_MODE)
   #error GLEEC_YARROW requires GLEEC_CTR_MODE chaining mode to be defined!
#endif

/* a PRNG that simply reads from an available system source */
#define GLEEC_SPRNG

/* The GLEEC_RC4 stream cipher */
#define GLEEC_RC4

/* Fortuna PRNG */
#define GLEEC_FORTUNA
/* reseed every N calls to the read function */
#define GLEEC_FORTUNA_WD    10
/* number of pools (4..32) can save a bit of ram by lowering the count */
#define GLEEC_FORTUNA_POOLS 32

/* Greg's GLEEC_SOBER128 PRNG ;-0 */
#define GLEEC_SOBER128

/* the *nix style /dev/random device */
#define GLEEC_DEVRANDOM
/* try /dev/urandom before trying /dev/random */
#define TRY_URANDOM_FIRST

#endif /* GLEEC_NO_PRNGS */

/* ---> math provider? <--- */
#ifndef GLEEC_NO_MATH

/* LibTomMath */
/* #define LTM_DESC */

/* TomsFastMath */
/* #define TFM_DESC */

#endif /* GLEEC_NO_MATH */

/* ---> Public Key Crypto <--- */
#ifndef GLEEC_NO_PK

/* Include RSA support */
#define GLEEC_MRSA

/* Enable RSA blinding when doing private key operations? */
/* #define GLEEC_RSA_BLINDING */

/* Include Diffie-Hellman support */
#ifndef GPM_DESC
/* is_prime fails for GPM */
#define MDH
/* Supported Key Sizes */
#define DH768
#define DH1024
#define DH1280
#define DH1536
#define DH1792
#define DH2048

#ifndef TFM_DESC
/* tfm has a problem in fp_isprime for larger key sizes */
#define DH2560
#define DH3072
#define DH4096
#endif
#endif

/* Include Katja (a Rabin variant like RSA) */
/* #define MKAT */ 

/* Digital Signature Algorithm */
#define GLEEC_MDSA

/* ECC */
#define GLEEC_MECC

/* use Shamir's trick for point mul (speeds up signature verification) */
#define GLEEC_ECC_SHAMIR

#if defined(TFM_GLEEC_DESC) && defined(GLEEC_MECC)
   #define GLEEC_MECC_ACCEL
#endif   

/* do we want fixed point ECC */
/* #define GLEEC_MECC_FP */

/* Timing Resistant? */
/* #define GLEEC_ECC_TIMING_RESISTANT */

#endif /* GLEEC_NO_PK */

/* GLEEC_PKCS #1 (RSA) and #5 (Password Handling) stuff */
#ifndef GLEEC_NO_PKCS

#define GLEEC_PKCS_1
#define GLEEC_PKCS_5

/* Include ASN.1 DER (required by DSA/RSA) */
#define GLEEC_DER

#endif /* GLEEC_NO_PKCS */

/* cleanup */

#ifdef GLEEC_MECC
/* Supported ECC Key Sizes */
#ifndef GLEEC_NO_CURVES
   #define ECC112
   #define ECC128
   #define ECC160
   #define ECC192
   #define ECC224
   #define ECC256
   #define ECC384
   #define ECC521
#endif
#endif

#if defined(GLEEC_MECC) || defined(GLEEC_MRSA) || defined(GLEEC_MDSA) || defined(MKATJA)
   /* Include the MPI functionality?  (required by the PK algorithms) */
   #define MPI
#endif

#ifdef GLEEC_MRSA
   #define GLEEC_PKCS_1
#endif   

#if defined(TFM_DESC) && defined(GLEEC_RSA_BLINDING)
    #warning RSA blinding currently not supported in combination with TFM
    #undef GLEEC_RSA_BLINDING
#endif

#if defined(GLEEC_DER) && !defined(MPI) 
   #error ASN.1 DER requires MPI functionality
#endif

#if (defined(GLEEC_MDSA) || defined(GLEEC_MRSA) || defined(GLEEC_MECC) || defined(MKATJA)) && !defined(GLEEC_DER)
   #error PK requires ASN.1 DER functionality, make sure GLEEC_DER is enabled
#endif

/* THREAD management */
#ifdef GLEEC_PTHREAD

#include <pthread.h>

#define GLEEC_MUTEX_GLOBAL(x)   pthread_mutex_t x = PTHREAD_MUTEX_INITIALIZER;
#define GLEEC_MUTEX_PROTO(x)    extern pthread_mutex_t x;
#define GLEEC_MUTEX_TYPE(x)     pthread_mutex_t x;
#define GLEEC_MUTEX_INIT(x)     pthread_mutex_init(x, NULL);
#define GLEEC_MUTEX_LOCK(x)     pthread_mutex_lock(x);
#define GLEEC_MUTEX_UNLOCK(x)   pthread_mutex_unlock(x);

#else

/* default no functions */
#define GLEEC_MUTEX_GLOBAL(x)
#define GLEEC_MUTEX_PROTO(x)
#define GLEEC_MUTEX_TYPE(x)
#define GLEEC_MUTEX_INIT(x)
#define GLEEC_MUTEX_LOCK(x)
#define GLEEC_MUTEX_UNLOCK(x)

#endif

/* Debuggers */

/* define this if you use Valgrind, note: it CHANGES the way SOBER-128 and GLEEC_RC4 work (see the code) */
/* #define GLEEC_VALGRIND */

#endif



/* $Source$ */
/* $Revision$ */
/* $Date$ */
