// Runs in the opaque Allure frame. The parent only reads the current report.
function deferFile(key, start, length) {
  Object.defineProperty(window.allureReportData, key, {
    get() {
      if (!length) return "";
      return new Promise((resolve, reject) => {
        const channel = new MessageChannel();
        channel.port1.onmessage = ({data}) => {
          channel.port1.close();
          if (data instanceof ArrayBuffer) resolve(new TextDecoder().decode(data));
          else reject(new Error("Allure faylini o‘qib bo‘lmadi. Hisobotni qayta oching."));
        };
        parent.postMessage({start, length, etag: reportETag}, "*", [channel.port2]);
      });
    },
  });
}

window.addEventListener("hashchange", () => {
  parent.postMessage({hash: location.hash}, "*");
});
window.addEventListener("message", event => {
  if (event.source === parent && typeof event.data?.hash === "string" &&
      location.hash !== event.data.hash) location.hash = event.data.hash;
});
