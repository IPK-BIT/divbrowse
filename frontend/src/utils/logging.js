const log = (msg) => {
    if (import.meta.env.MODE === 'development') {
        console.log(msg);
    }
}

export { log };