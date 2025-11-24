// Control simple para abrir/cerrar el modal de filtros (sin Bootstrap)
(function(){
  function qs(sel, root=document){ return root.querySelector(sel); }
  function qsa(sel, root=document){ return Array.from(root.querySelectorAll(sel)); }

  const openBtns = qsa('[data-action="open-filters"]');
  const modal = qs('#filtrosModal');
  if(!modal) return;
  const backdrop = modal.querySelector('.modal-backdrop');
  const closeables = qsa('[data-action="close"]', modal);

  function openModal(){
    modal.classList.remove('modal-hidden');
    modal.setAttribute('aria-hidden','false');
    document.body.style.overflow = 'hidden';
  }
  function closeModal(){
    modal.classList.add('modal-hidden');
    modal.setAttribute('aria-hidden','true');
    document.body.style.overflow = '';
  }

  openBtns.forEach(b => b.addEventListener('click', openModal));
  closeables.forEach(c => c.addEventListener('click', closeModal));
  backdrop && backdrop.addEventListener('click', closeModal);

  // cerrar con Escape
  document.addEventListener('keydown', function(e){ if(e.key === 'Escape') closeModal(); });
})();
