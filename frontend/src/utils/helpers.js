const debounce = (callback, wait) => {
    let timeoutId = null;
    return (...args) => {
        window.clearTimeout(timeoutId);
        timeoutId = window.setTimeout(() => {
        callback.apply(null, args);
        }, wait);
    };
}

const isHetero = arr => arr.some(item => item !== arr[0]);

const numberOfAltAllelesFactory = {
    getFunction: function(_ploidy) {
        let ploidy = _ploidy;
        
        const numberOfAlternateAlleles = (calls) => {
            if (ploidy == 2) {
                let variantType = 2;
                if (calls[0] == -1) {
                    variantType = -1;
                } else if (isHetero(calls)) {
                    variantType = 1;
                } else if (calls.reduce((a, b) => a + b, 0) === 0) {
                    variantType = 0;
                }
                return variantType;
            }
        
            if (ploidy == 1) {
                let variantType = 2;
                if (calls === 0) {
                    variantType = 0;
                }
                return variantType;
            }
        }
    
        return numberOfAlternateAlleles;
    }
}

export { debounce, numberOfAltAllelesFactory };