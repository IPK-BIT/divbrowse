import App from './App.svelte';

export function startApp(containerId, config) {

    let _containerId = '#'+containerId;
    
    //let _config = JSON.parse(JSON.stringify(config));
    let _config = Object.assign({}, config);

    let app = new App({
        target: document.querySelector(_containerId),
        props: {
            config: _config,
            appId: 'divbrowse-'+containerId,
        }
    });
    return app;
}