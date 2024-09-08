import ViewModel from './viewmodel.js';
import DataLayer from './data.js';

const View = {
    init() {
        this.bindEvents();
        this.initializeTable();
        ViewModel.refreshData();  // 确保初始调用
    },

    bindEvents() {
        $('#applyFilter').click(() => this.handleApplyFilter());
        $('#resetFilter').click(() => this.handleResetFilter());
        $('#prevPage').click(() => this.handlePrevPage());
        $('#nextPage').click(() => this.handleNextPage());
        $('#goToPage').click(() => this.handleGoToPage());
        $('#addNewBtn').click(() => this.showAddModal());
        $('#saveChanges').click(() => this.handleSaveChanges());
        $('#confirmDelete').click(() => this.handleConfirmDelete());
        $('#setStatusBtn').click(() => this.showStatusChangeModal());
        $('#confirmStatusChange').click(() => this.handleConfirmStatusChange());
        $('#deleteSelectedBtn').click(() => this.handleDeleteSelected());
        $('#selectAll').change(() => this.handleSelectAll());
        $(document).on('change', '.rowCheckbox', () => this.handleRowCheckboxChange());
    },

    initializeTable() {
        $("#dataTable").tablesorter({
            headers: {
                0: { sorter: false },
                8: { sorter: false }
            },
            sortList: [[7,1]],
            widgets: ['zebra'],
            widgetOptions: {
                zebra: ['even', 'odd'],
            },
        }).on('sortEnd', (e, table) => this.handleSort(table));
    },

    async handleApplyFilter() {
        const filterParams = {
            status: $("#statusFilter").val(),
            minAmount: $("#minAmount").val(),
            maxAmount: $("#maxAmount").val()
        };
        await ViewModel.applyFilter(filterParams);
        this.updateTable();
    },

    async handleResetFilter() {
        $("#statusFilter").val("");
        $("#minAmount").val("");
        $("#maxAmount").val("");
        await ViewModel.applyFilter({});
        this.updateTable();
    },

    async handlePrevPage() {
        if (DataLayer.currentPage > 1) {
            DataLayer.currentPage--;
            await ViewModel.changePage(DataLayer.currentPage);
            this.updateTable();
        }
    },

    async handleNextPage() {
        if (DataLayer.currentPage < DataLayer.totalPages) {
            DataLayer.currentPage++;
            await ViewModel.changePage(DataLayer.currentPage);
            this.updateTable();
        }
    },

    async handleGoToPage() {
        const pageNumber = parseInt($("#pageInput").val());
        if (pageNumber >= 1 && pageNumber <= DataLayer.totalPages && pageNumber !== DataLayer.currentPage) {
            DataLayer.currentPage = pageNumber;
            await ViewModel.changePage(pageNumber);
            this.updateTable();
        } else {
            alert("Invalid page number. Please enter a number between 1 and " + DataLayer.totalPages);
        }
    },

    async handleSort(table) {
        const sortList = table.config.sortList;
        if (sortList.length > 0) {
            const column = this.getColumnName(sortList[0][0]);
            const order = sortList[0][1] === 0 ? 'asc' : 'desc';
            if (column !== DataLayer.currentSortColumn || order !== DataLayer.currentSortOrder) {
                await ViewModel.changeSort(column, order);
                this.updateTable();
            }
        }
    },

    getColumnName(index) {
        const columnMap = {
            1: 'referenceNo', 2: 'from', 3: 'to', 4: 'amount',
            5: 'messageType', 6: 'status', 7: 'lastUpdate'
        };
        return columnMap[index] || 'lastUpdate';
    },

    updateTable() {
        $("#dataTable tbody").empty();
        DataLayer.transfers.forEach(transfer => {
            const row = this.createTableRow(transfer);
            $("#dataTable tbody").append(row);
        });

        this.updatePagination();
        this.updateTableInfo();
        this.updateFloatingBar();
        $("#dataTable").trigger("update");
    },

    createTableRow(transfer) {
        return `
            <tr>
                <td><input type="checkbox" class="rowCheckbox" data-id="${transfer.id}"></td>
                <td>${transfer.referenceNo}</td>
                <td>${transfer.from}</td>
                <td>${transfer.to}</td>
                <td>${transfer.amount}</td>
                <td>${transfer.messageType}</td>
                <td>${transfer.status}</td>
                <td>${new Date(transfer.lastUpdate).toLocaleString()}</td>
                <td>
                    <button class="edit btn btn-outline-primary me-1" data-id="${transfer.id}">Edit</button>
                    <button class="delete btn btn-outline-danger" data-id="${transfer.id}">Delete</button>
                </td>
            </tr>
        `;
    },

    updatePagination() {
        $("#pageInput").val(DataLayer.currentPage);
        $("#prevPage").prop("disabled", DataLayer.currentPage === 1);
        $("#nextPage").prop("disabled", DataLayer.currentPage === DataLayer.totalPages);
        $("#pageInfo").text(`Page ${DataLayer.currentPage} of ${DataLayer.totalPages}`);
    },

    updateTableInfo() {
        const start = (DataLayer.currentPage - 1) * DataLayer.itemsPerPage + 1;
        const end = Math.min(DataLayer.currentPage * DataLayer.itemsPerPage, DataLayer.totalItems);
        $("#dataInfo").text(`Showing ${start} to ${end} of ${DataLayer.totalItems} entries`);
    },

    updateFloatingBar() {
        const selectedCheckboxes = $(".rowCheckbox:checked");
        if (selectedCheckboxes.length > 0) {
            const selectedIds = selectedCheckboxes.map(function() {
                return $(this).data('id');
            }).get();
            const selectedItems = DataLayer.transfers.filter(item => selectedIds.includes(item.id));
            const allActive = selectedItems.every(item => item.status === "Active");
            const allInactive = selectedItems.every(item => item.status === "Inactive");

            $("#selectedCount").text(`${selectedItems.length} transfer(s) selected`);
            $("#calculateBtn").show();
            $("#calculationResult").text('');

            if (allActive || allInactive) {
                $("#setStatusBtn").text(allActive ? "Set Inactive" : "Set Active").show();
                $("#statusWarning").hide();
            } else {
                $("#setStatusBtn").hide();
                $("#statusWarningText").text('Selected transfers have different statuses');
                $("#statusWarning").show();
            }

            $("#floatingBar").show();
        } else {
            $("#floatingBar").hide();
        }
    },

    showAddModal() {
        $('#editModalLabel').text('Add New Transfer');
        $('#editForm')[0].reset();
        $('#editModal').modal('show');
    },

    async handleSaveChanges() {
        const transferData = {
            referenceNo: $('#referenceNo').val(),
            from: $('#from').val(),
            to: $('#to').val(),
            amount: $('#amount').val(),
            messageType: $('#messageType').val(),
            status: $('input[name="status"]:checked').val(),
        };

        if ($('#editModalLabel').text() === 'Edit Transfer') {
            transferData.id = $('#editForm').data('id');
            await ViewModel.updateTransfer(transferData);
        } else {
            await ViewModel.addNewTransfer(transferData);
        }

        $('#editModal').modal('hide');
        this.updateTable();
    },

    async handleConfirmDelete() {
        const id = $('#deleteModal').data('id');
        await ViewModel.deleteTransfer(id);
        $('#deleteModal').modal('hide');
        this.updateTable();
    },

    showStatusChangeModal() {
        const newStatus = $("#setStatusBtn").text() === "Set Active" ? "Active" : "Inactive";
        const selectedIds = $(".rowCheckbox:checked").map(function() {
            return $(this).data('id');
        }).get();
        const selectedItems = DataLayer.transfers.filter(item => selectedIds.includes(item.id));
        const totalAmount = this.calculateTotalAmount(selectedItems);

        $("#selectedAmount").text(`$${totalAmount.toFixed(2)}`);
        $("#statusChangeModalLabel").text($("#setStatusBtn").text());
        $("#statusChangeModal").modal('show');
    },

    async handleConfirmStatusChange() {
        const newStatus = $("#statusChangeModalLabel").text() === "Set Active" ? "Active" : "Inactive";
        const selectedIds = $(".rowCheckbox:checked").map(function() {
            return $(this).data('id');
        }).get();

        await ViewModel.bulkUpdateStatus(selectedIds, newStatus);
        $("#statusChangeModal").modal('hide');
        this.updateTable();
    },

    calculateTotalAmount(items) {
        return items.reduce((sum, item) => {
            const amount = parseFloat(item.amount.replace('$', '').replace(',', ''));
            return sum + (isNaN(amount) ? 0 : amount);
        }, 0);
    },

    handleSelectAll() {
        $(".rowCheckbox").prop('checked', $("#selectAll").prop('checked'));
        this.updateFloatingBar();
    },

    handleRowCheckboxChange() {
        const allChecked = $(".rowCheckbox:not(:checked)").length === 0;
        $("#selectAll").prop('checked', allChecked);
        this.updateFloatingBar();
    },

    async handleDeleteSelected() {
        const selectedIds = $(".rowCheckbox:checked").map(function() {
            return $(this).data('id');
        }).get();

        if (selectedIds.length > 0) {
            const confirmDelete = confirm(`Are you sure you want to delete ${selectedIds.length} selected transfer(s)?`);
            if (confirmDelete) {
                for (const id of selectedIds) {
                    await ViewModel.deleteTransfer(id);
                }
                this.updateTable();
            }
        }
    }
};

export default View;