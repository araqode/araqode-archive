import { h, render } from 'preact';
import Router from './router.jsx';
import UrlPrefixContext from './context/url-prefix.jsx';

function getPrefixFromLocation() {
    let path = window.location.pathname;

    // Remove trailing slash if present
    if (path.endsWith('/')) {
        path = path.slice(0, -1);
    }
    
    return path;
}

const urlPrefix = getPrefixFromLocation();

render(
    <UrlPrefixContext.Provider value={urlPrefix}>
        <Router />
    </UrlPrefixContext.Provider>,
    document.body
);
