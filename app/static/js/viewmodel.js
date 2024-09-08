// viewmodel.js
import DataLayer from './data.js';
import Service from './service.js';

const ViewModel = {
    async applyFilter(filterParams) {
        DataLayer.currentPage = 1;
        await Service.loadData({ filter: filterParams });
    },

    async changePage(newPage) {
        if (newPage !== DataLayer.currentPage) {
            DataLayer.currentPage = newPage;
            await Service.loadData();
        }
    },

    async changeSort(column, order) {
        if (column !== DataLayer.currentSortColumn || order !== DataLayer.currentSortOrder) {
            DataLayer.currentSortColumn = column;
            DataLayer.currentSortOrder = order;
            await Service.loadData();
        }
    },

    async addNewTransfer(transfer) {
        await Service.addTransfer(transfer);
        await this.refreshData();
    },

    async updateTransfer(transfer) {
        await Service.updateTransfer(transfer);
        await this.refreshData();
    },

    async deleteTransfer(id) {
        await Service.deleteTransfer(id);
        await this.refreshData();
    },

    async bulkUpdateStatus(ids, status) {
        await Service.bulkUpdateStatus(ids, status);
        await this.refreshData();
    },

    async refreshData() {
        await Service.loadData();
        await this.updateSummary();
    },

    async updateSummary() {
        const summary = await Service.fetchSummary();
        // Update UI with new summary data
        $("#totalAmount").text(`$${summary.totalAmount.toFixed(2)}`);
        $("#totalCount").text(summary.totalCount);
        $("#activeAmount").text(`$${summary.activeAmount.toFixed(2)}`);
        $("#inactiveAmount").text(`$${summary.inactiveAmount.toFixed(2)}`);
        $("#activeCount").text(summary.activeCount);
        $("#inactiveCount").text(summary.inactiveCount);
    }
};

export default ViewModel;