const isHetero = arr => arr.some(item => item !== arr[0]);

/*const numberOfAlternateAlleles = (calls) => {
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
}*/

const getFuncNumberOfAlternateAllelesByPloidy = (_ploidy) => {
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

export { numberOfAltAllelesFactory, getFuncNumberOfAlternateAllelesByPloidy };