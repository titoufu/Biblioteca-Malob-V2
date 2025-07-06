self.addEventListener('install', event => {
  console.log('Service Worker: Installed');
  event.waitUntil(self.skipWaiting()); // força ativação imediata
});

self.addEventListener('activate', event => {
  event.waitUntil(self.clients.claim()); // pega controle das páginas atuais
});