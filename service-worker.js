const CACHE_NAME = 'v1';

self.addEventListener('install', event => {
  console.log(`Service Worker: Instalado - Versão ${CACHE_NAME}`);
  event.waitUntil(self.skipWaiting());
});

self.addEventListener('activate', event => {
  event.waitUntil(self.clients.claim());
});