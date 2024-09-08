// service.js
import DataLayer from './data.js';

const Service = {
    async loadData(params = {}) {
        const response = await fetch('/api/data', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                action: 'get',
                filter: params.filter || {},
                sort: {
                    field: DataLayer.currentSortColumn,
                    order: DataLayer.currentSortOrder
                },
                page: DataLayer.currentPage,
                itemsPerPage: DataLayer.itemsPerPage
            })
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const data = await response.json();
        DataLayer.transfers = data.data;
        DataLayer.totalItems = data.totalItems;
        DataLayer.totalPages = data.totalPages;
        return data;
    },

    async fetchSummary() {
        const response = await fetch('/api/summary', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({})
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        return await response.json();
    },

    async addTransfer(transfer) {
        const response = await fetch('/api/add_item', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(transfer)
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        return await response.json();
    },

    async updateTransfer(transfer) {
        const response = await fetch(`/api/update_item/${transfer.id}`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(transfer)
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        return await response.json();
    },

    async deleteTransfer(id) {
        const response = await fetch(`/api/delete_item/${id}`, {
            method: 'DELETE'
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        return await response.json();
    },

    async bulkUpdateStatus(ids, status) {
        const response = await fetch('/api/bulk_update', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ ids, status })
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        return await response.json();
    }
};

export default Service;