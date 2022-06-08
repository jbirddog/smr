// https://www.30secondsofcode.org/js/s/slugify
export const slugifyString = ((str) => {
  str
    .toLowerCase()
    .trim()
    .replace(/[^\w\s-]/g, '')
    .replace(/[\s_-]+/g, '-')
    .replace(/^-+|-+$/g, '');
});
