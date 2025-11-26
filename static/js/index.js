window.app = Vue.createApp({
  el: '#vue',
  mixins: [windowMixin],
  delimiters: ['${', '}'],
  data: function () {
    return {
      stats: {
        total_users: 0,
        total_balance: 0,
        total_spent: 0,
        total_deposited: 0,
        total_messages: 0
      },

      // User Management
      userList: [],
      userTable: {
        search: '',
        loading: false,
        columns: [
          {name: 'npub', align: 'left', label: 'Npub', field: 'npub', sortable: true},
          {name: 'balance_sats', align: 'right', label: 'Balance (sats)', field: 'balance_sats', sortable: true},
          {name: 'total_spent', align: 'right', label: 'Total Spent', field: 'total_spent', sortable: true},
          {name: 'total_deposited', align: 'right', label: 'Total Deposited', field: 'total_deposited', sortable: true},
          {name: 'message_count', align: 'right', label: 'Messages', field: 'message_count', sortable: true},
          {name: 'updated_at', align: 'left', label: 'Last Activity', field: 'updated_at', sortable: true}
        ],
        pagination: {
          sortBy: 'updated_at',
          descending: true,
          page: 1,
          rowsPerPage: 10,
          rowsNumber: 10
        }
      },

      // User Details Dialog
      userDetailsDialog: {
        show: false,
        user: null,
        transactions: []
      },

      // Recent Transactions
      transactionList: [],
      transactionTable: {
        loading: false,
        columns: [
          {name: 'created_at', align: 'left', label: 'Date', field: 'created_at', sortable: true},
          {name: 'npub', align: 'left', label: 'User', field: 'npub', sortable: true},
          {name: 'type', align: 'left', label: 'Type', field: 'type', sortable: true},
          {name: 'amount_sats', align: 'right', label: 'Amount (sats)', field: 'amount_sats', sortable: true},
          {name: 'memo', align: 'left', label: 'Memo', field: 'memo', sortable: false}
        ],
        pagination: {
          sortBy: 'created_at',
          descending: true,
          page: 1,
          rowsPerPage: 10,
          rowsNumber: 10
        }
      }
    }
  },

  computed: {
    filteredUsers() {
      if (!this.userTable.search) {
        return this.userList
      }
      const search = this.userTable.search.toLowerCase()
      return this.userList.filter(user =>
        user.npub.toLowerCase().includes(search)
      )
    },
    publicPageUrl() {
      // Use first wallet as default for public page URL
      if (this.g.user && this.g.user.wallets && this.g.user.wallets.length > 0) {
        return `${window.location.origin}/bitsatcredit/${this.g.user.wallets[0].id}`
      }
      return `${window.location.origin}/bitsatcredit/YOUR_WALLET_ID`
    }
  },

  methods: {
    //////////////// Stats ////////////////////////
    async getStats() {
      try {
        const {data} = await LNbits.api.request(
          'GET',
          '/bitsatcredit/api/v1/stats',
          null
        )
        this.stats = data
      } catch (error) {
        LNbits.utils.notifyApiError(error)
      }
    },

    //////////////// Users ////////////////////////
    async getUsers() {
      try {
        this.userTable.loading = true
        const {data} = await LNbits.api.request(
          'GET',
          '/bitsatcredit/api/v1/users?limit=100&offset=0',
          null
        )
        this.userList = data
        this.userTable.pagination.rowsNumber = data.length
      } catch (error) {
        LNbits.utils.notifyApiError(error)
      } finally {
        this.userTable.loading = false
      }
    },

    async showUserDetails(user) {
      try {
        this.userDetailsDialog.user = user
        this.userDetailsDialog.show = true

        // Fetch user's transaction history
        const {data} = await LNbits.api.request(
          'GET',
          `/bitsatcredit/api/v1/user/${user.npub}/transactions`,
          null
        )
        this.userDetailsDialog.transactions = data
      } catch (error) {
        LNbits.utils.notifyApiError(error)
      }
    },

    async exportUsersCSV() {
      await LNbits.utils.exportCSV(
        this.userTable.columns,
        this.userList,
        'bitsatcredit_users_' + new Date().toISOString().slice(0, 10) + '.csv'
      )
    },

    //////////////// Transactions ////////////////////////
    async getRecentTransactions() {
      try {
        this.transactionTable.loading = true
        const {data} = await LNbits.api.request(
          'GET',
          '/bitsatcredit/api/v1/transactions/recent?limit=50',
          null
        )
        this.transactionList = data
        this.transactionTable.pagination.rowsNumber = data.length
      } catch (error) {
        LNbits.utils.notifyApiError(error)
      } finally {
        this.transactionTable.loading = false
      }
    },

    //////////////// Utils ////////////////////////
    dateFromNow(date) {
      return moment(date).fromNow()
    },

    copyPublicUrl() {
      navigator.clipboard.writeText(this.publicPageUrl)
      Quasar.Notify.create({
        type: 'positive',
        message: 'Public URL copied to clipboard',
        timeout: 1000
      })
    }
  },

  ///////////////////////////////////////////////////
  //////LIFECYCLE FUNCTIONS RUNNING ON PAGE LOAD/////
  ///////////////////////////////////////////////////
  async created() {
    await this.getStats()
    await this.getUsers()
    await this.getRecentTransactions()
  }
})
