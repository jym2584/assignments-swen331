const sanitizeHTML = require('sanitize-html');

// Sanity check method to make sure you have your environment up and running.
function sum(a, b) {
  return a + b;
}

/*
  Valid book titles in this situation can include:
    - Cannot be any form of "Boaty McBoatface", case insensitive
    - English alphabet characters
    - Arabic numerals
    - Spaces, but no other whitespace like tabs or newlines
    - Quotes, both single and double
    - Hyphens
    - No leading or trailing whitespace
    - No newlines or tabs
*/
function isTitle(str){
  /**
   * Blocklist indexes:
   * 0: any instances of bloaty mcboatface
   * 1: trailing whitespace after a string sequence
   * 2: trailing whitespace before a string sequence
   * 3: special escape sequences
   */
  const blocklist = [/Boaty McboatFace/, /\s$/, /^\s/, /[\t\n\r\f\v\0]/];
  for (let i = 0; i < blocklist.length; i++) {
    const regex = new RegExp(blocklist[i], 'i');
    if (regex.test(str)) {
      return false;
    }
  }
  // also incldue emojis, not sure why they're failing on the blocklist however
  if (/\p{Extended_Pictographic}/u.test(str)) {
      return false;
  }

  /**
   * Allow list indexes:
   * 0: include mostly everything valid from an american keyboard (except slashes)
   * 1: i18n characters
   */
  const allowlist = [/^[A-Za-z0-9"' -]+$/, /[\p{Letter}\p{Mark}\s-]+/gu];
  for (let i = 0; i < allowlist.length; i++) {
    const regex = new RegExp(allowlist[i], 'i');
    if (regex.test(str)) {
      return true;
    }
  }


  return false;
}

/*
  Are the two titles *effectively* the same when searching?

  This function will be used as part of a search feature, so it should be
  flexible when dealing with diacritics and ligatures.

  Input: two raw strings
  Output: true if they are "similar enough" to each other

  We define two strings as the "similar enough" as:

    * ignore leading and trailing whitespace
    * same sequence of "letters", ignoring diacritics and ligatures, that is:
      anything that is NOT a letter in the UTF-8 decomposed form is removed
    * Ligature "\u00E6" or æ is equivalent to "ae"
    * German character "\u1E9E" or ẞ is equivalent to "ss"
*/
function isSameTitle(strA, strB){
  return false;
}

/*
  Page range string.

  Count, inclusively, the number of pages mentioned in the string.

  This is modeled after the string you can use to specify page ranges in
  books, or in a print dialog.

  Example page ranges, copied from our test cases:
    1          ===> 1 page
    p3         ===> 1 page
    1-2        ===> 2 pages
    10-100     ===> 91 pages
    1-3,5-6,9  ===> 6 pages
    1-3,5-6,p9 ===> 6 pages

  A range that goes DOWN still counts, but is never negative.

  Whitespace is allowed anywhere in the string with no effect.

  If the string is over 1000 characters, return undefined
  If the string returns in NaN, return undefined
  If the string does not properly fit the format, return 0

*/
function countPages(rawStr){
  return false;
}

/*
  Perform a best-effort cleansing of the page number.
  Given: a raw string
  Returns: an integer, ignoring leading and trailing whitespace. And it can have p in front of it.
*/
function cleanPageNum(str){
  return false;
}


/*
  Given a string, return another string that is safe for embedding into HTML.
    * Use the sanitize-html library: https://www.npmjs.com/package/sanitize-html
    * Configure it to *only* allow <b> tags and <i> tags
      (Read the README to learn how to do this)
*/
function cleanForHTML(dirty) {
  return dirty;
}


// Too all my JS nitpickers...
// We are using CommonJS modules because that's what Jest currently best supports
// But, the more modern, preferred way is ES6 modules, i.e. "import/export"
module.exports = {
  sum,
  isTitle,
  countPages,
  cleanPageNum,
  isSameTitle,
  cleanForHTML,
};
