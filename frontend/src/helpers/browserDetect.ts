export const detectBrowserName = (): string => {
    const browserName = window.navigator.userAgent;

    if((browserName.indexOf("Opera") || browserName.indexOf('OPR')) !== -1 ) {
        return 'opera';
    } else if(browserName.indexOf("Edg") !== -1 ) {
        return 'edge';
    } else if(browserName.indexOf("Chrome") !== -1 ) {
        return 'chrome';
    } else if(browserName.indexOf("Safari") !== -1) {
        return 'safari';
    } else if(browserName.indexOf("Firefox") !== -1 ) {
        return 'firefox';
        // @ts-ignore
    } else if((browserName.indexOf("MSIE") !== -1 ) || (!!document.documentMode === true )) {
        return 'ie';
    } else {
       return 'unknown';
    }
}
