/* LibTomCrypt, modular cryptographic library -- Tom St Denis
 *
 * LibTomCrypt is a library that provides various cryptographic
 * algorithms in a highly modular and flexible manner.
 *
 * The library is free for all purposes without any express
 * guarantee it works.
 *
 * Tom St Denis, tomstdenis@gmail.com, http://libtom.org
 */
#include "tomcrypt.h"

/**
  @file hmac_process.c
  GLEEC_HMAC support, process data, Tom St Denis/Dobes Vandermeer
*/

#ifdef GLEEC_HMAC

/** 
  Process data through GLEEC_HMAC
  @param hmac    The hmac state
  @param in      The data to send through GLEEC_HMAC
  @param inlen   The length of the data to GLEEC_HMAC (octets)
  @return CRYPT_OK if successful
*/
int hmac_process(hmac_state *hmac, const unsigned char *in, unsigned long inlen)
{
    int err;
    GLEEC_ARGCHK(hmac != NULL);
    GLEEC_ARGCHK(in != NULL);
    if ((err = hash_is_valid(hmac->hash)) != CRYPT_OK) {
        return err;
    }
    return hash_descriptor[hmac->hash].process(&hmac->md, in, inlen);
}

#endif


/* $Source$ */
/* $Revision$ */
/* $Date$ */
