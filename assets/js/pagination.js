/* pagination.js - Composant de pagination réutilisable */

export class Pagination {
  constructor({
    container,
    items = [],
    itemsPerPage = 50,
    renderItem,
    onPageChange = null
  }) {
    this.container = typeof container === 'string'
      ? document.getElementById(container)
      : container;
    this.items = items;
    this.itemsPerPage = itemsPerPage;
    this.renderItem = renderItem;
    this.onPageChange = onPageChange;
    this.currentPage = 1;
    this.paginationContainer = null;
  }

  get totalPages() {
    return Math.ceil(this.items.length / this.itemsPerPage);
  }

  get currentItems() {
    const start = (this.currentPage - 1) * this.itemsPerPage;
    const end = start + this.itemsPerPage;
    return this.items.slice(start, end);
  }

  setItems(items) {
    this.items = items;
    this.currentPage = 1;
    this.render();
  }

  goToPage(page) {
    if (page < 1 || page > this.totalPages) return;
    this.currentPage = page;
    this.render();
    this.onPageChange?.(page);
    // Scroll to top of container
    this.container.scrollIntoView({ behavior: 'smooth', block: 'start' });
  }

  render() {
    this.renderItems();
    this.renderPagination();
  }

  renderItems() {
    this.container.innerHTML = '';
    const fragment = document.createDocumentFragment();

    this.currentItems.forEach((item, index) => {
      const element = this.renderItem(item, index);
      if (element) {
        fragment.appendChild(element);
      }
    });

    this.container.appendChild(fragment);
  }

  renderPagination() {
    // Supprimer l'ancienne pagination si elle existe
    if (this.paginationContainer) {
      this.paginationContainer.remove();
    }

    // Ne pas afficher si une seule page
    if (this.totalPages <= 1) return;

    this.paginationContainer = document.createElement('div');
    this.paginationContainer.className = 'pagination';

    const fragment = document.createDocumentFragment();

    // Bouton précédent
    const prevBtn = this.createButton('‹', () => this.goToPage(this.currentPage - 1));
    prevBtn.disabled = this.currentPage === 1;
    prevBtn.className = 'pagination-btn pagination-prev';
    fragment.appendChild(prevBtn);

    // Numéros de pages
    const pageNumbers = this.getPageNumbers();
    pageNumbers.forEach(pageNum => {
      if (pageNum === '...') {
        const ellipsis = document.createElement('span');
        ellipsis.className = 'pagination-ellipsis';
        ellipsis.textContent = '...';
        fragment.appendChild(ellipsis);
      } else {
        const btn = this.createButton(pageNum, () => this.goToPage(pageNum));
        btn.className = `pagination-btn ${pageNum === this.currentPage ? 'active' : ''}`;
        fragment.appendChild(btn);
      }
    });

    // Bouton suivant
    const nextBtn = this.createButton('›', () => this.goToPage(this.currentPage + 1));
    nextBtn.disabled = this.currentPage === this.totalPages;
    nextBtn.className = 'pagination-btn pagination-next';
    fragment.appendChild(nextBtn);

    // Info page
    const info = document.createElement('span');
    info.className = 'pagination-info';
    info.textContent = `Page ${this.currentPage}/${this.totalPages}`;
    fragment.appendChild(info);

    this.paginationContainer.appendChild(fragment);

    // Insérer après le container
    this.container.parentNode.insertBefore(
      this.paginationContainer,
      this.container.nextSibling
    );
  }

  getPageNumbers() {
    const pages = [];
    const total = this.totalPages;
    const current = this.currentPage;
    const delta = 2; // Nombre de pages autour de la page courante

    if (total <= 7) {
      // Afficher toutes les pages
      for (let i = 1; i <= total; i++) pages.push(i);
    } else {
      // Toujours afficher la première page
      pages.push(1);

      if (current > delta + 2) {
        pages.push('...');
      }

      // Pages autour de la page courante
      const start = Math.max(2, current - delta);
      const end = Math.min(total - 1, current + delta);

      for (let i = start; i <= end; i++) {
        pages.push(i);
      }

      if (current < total - delta - 1) {
        pages.push('...');
      }

      // Toujours afficher la dernière page
      pages.push(total);
    }

    return pages;
  }

  createButton(text, onClick) {
    const btn = document.createElement('button');
    btn.textContent = text;
    btn.addEventListener('click', onClick);
    return btn;
  }
}