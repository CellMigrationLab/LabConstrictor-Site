/* The installer's operating system (Windows or macOS): its first page and its place in the address (?os=macos), and the demo's part in the
   address (?demo=use). Nothing here draws or changes the state. */
(function (ns) {
  var d = ns.dom;
  var FIRST_PAGES = { windows: 'download', macos: 'mac-download' };

  /**
   * The first installer page of a system.
   * @param {string} os - 'windows' or 'macos'.
   * @returns {string} the data-page value to start on.
   * @throws {Error} for an unknown system.
   */
  function firstPage(os) {
    return d.lookup(FIRST_PAGES, os, 'system');
  }

  /**
   * The system the address asks for: ?os=macos opens the macOS installer; any other address opens the Windows one (the default).
   * @returns {string} 'macos' or 'windows'.
   */
  function fromAddress() {
    return new URLSearchParams(location.search).get('os') === 'macos' ? 'macos' : 'windows';
  }

  /**
   * Write the system into the address, replacing the history entry, so that a reload or a shared link opens the same installer.
   * @param {string} os - 'windows' or 'macos'.
   * @returns {void}
   */
  function remember(os) {
    var url = new URL(location.href);
    url.searchParams.set('os', os);
    history.replaceState(history.state, '', url);
  }

  /**
   * Write the demo's part into the address when it is not there yet, replacing the history entry, so that a reload or a shared link opens
   * the same part (also when the installer's last step opened the installed app).
   * @param {string} part - 'install' or 'use'.
   * @returns {void}
   */
  function rememberPart(part) {
    var url = new URL(location.href);
    if ((url.searchParams.get('demo') === 'use' ? 'use' : 'install') === part) { return; }
    url.searchParams.set('demo', part);
    history.replaceState(history.state, '', url);
  }

  ns.os = { firstPage: firstPage, fromAddress: fromAddress, remember: remember, rememberPart: rememberPart };
})(window.LCDemo = window.LCDemo || {});
