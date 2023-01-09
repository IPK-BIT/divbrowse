import App from './App.svelte';

const useShadowDOM = true;

function startApp(containerId, config) {

    let _containerId = '#'+containerId;
    let container = document.querySelector(_containerId);
    let target;

    if (useShadowDOM) {
        target = container.attachShadow({ mode: "open" });
    } else {
        target = container;
    }
    
    //let _config = JSON.parse(JSON.stringify(config));
    let _config = Object.assign({}, config);

    let app = new App({
        target: target,
        props: {
            config: _config,
            appId: 'divbrowse-'+containerId,
            rootElem: target
        }
    });
    return app;
}

window.divbrowse = {
    'startApp': startApp
}