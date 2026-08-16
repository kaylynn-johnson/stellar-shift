export function roundDecimals(num: number, places: number) {
    return Math.round(num * (10 ** places)) / (10 ** places);
}
