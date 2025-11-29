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
      selectedUsers: [],
      selectAll: false,
      userTable: {
        search: '',
        loading: false,
        columns: [
          {name: 'npub', align: 'left', label: 'Npub', field: 'npub', sortable: true},
          {name: 'balance_sats', align: 'right', label: 'Balance (sats)', field: 'balance_sats', sortable: true},
          {name: 'total_spent', align: 'right', label: 'Total Spent', field: 'total_spent', sortable: true},
          {name: 'total_deposited', align: 'right', label: 'Total Deposited', field: 'total_deposited', sortable: true},
          {name: 'message_count', align: 'right', label: 'Messages', field: 'message_count', sortable: true},
          {name: 'memo', align: 'left', label: 'Memo', field: 'memo', sortable: true},
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

      // Settings
      selectedWallet: null,
      walletOptions: [],
      externalUrl: '',
      pricePerMessage: 1,
      systemStatus: 'online',
      systemOnline: true,
      systemStatusMessage: '',

      // Add Credits Dialog
      addCreditsDialog: {
        show: false,
        npub: '',
        amount: null,
        memo: ''
      },

      // Create User Dialog
      createUserDialog: {
        show: false,
        npub: '',
        initialBalance: 0
      },

      // Edit Balance Dialog
      editBalanceDialog: {
        show: false,
        npub: '',
        currentBalance: 0,
        newBalance: 0,
        memo: ''
      },

      // Edit Memo Dialog
      editMemoDialog: {
        show: false,
        npub: '',
        memo: ''
      },

      // Bulk Add Credits Dialog
      bulkAddCreditsDialog: {
        show: false,
        amount: null,
        memo: ''
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
        user.npub.toLowerCase().includes(search) ||
        (user.memo && user.memo.toLowerCase().includes(search))
      )
    },
    publicPageUrl() {
      const baseUrl = this.externalUrl || window.location.origin

      let walletId = 'YOUR_WALLET_ID'

      if (this.selectedWallet?.value) {
        walletId = this.selectedWallet.value
      } else if (this.g?.user?.wallets && this.g.user.wallets.length > 0) {
        walletId = this.g.user.wallets[0].id
      }

      return `${baseUrl}/bitsatcredit/${walletId}`
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

    toggleSelectAll(value) {
      if (value) {
        this.selectedUsers = this.filteredUsers.map(u => u.npub)
      } else {
        this.selectedUsers = []
      }
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
      return moment(date * 1000).fromNow()
    },

    copyPublicUrl() {
      navigator.clipboard.writeText(this.publicPageUrl)
      Quasar.Notify.create({
        type: 'positive',
        message: 'Public URL copied to clipboard',
        timeout: 1000
      })
    },

    //////////////// Settings ////////////////////////
    loadWalletOptions() {
      if (this.g.user && this.g.user.wallets) {
        this.walletOptions = this.g.user.wallets.map(w => ({
          label: w.name,
          value: w.id
        }))
        if (this.walletOptions.length > 0 && !this.selectedWallet) {
          this.selectedWallet = this.walletOptions[0]
        }
      }
    },

    async saveWalletSetting() {
      if (this.selectedWallet) {
        localStorage.setItem('bitsatcredit_wallet_id', this.selectedWallet.value)
        Quasar.Notify.create({
          type: 'positive',
          message: 'Wallet setting saved',
          timeout: 1000
        })
      }
    },

    async saveExternalUrl() {
      localStorage.setItem('bitsatcredit_external_url', this.externalUrl || '')
      Quasar.Notify.create({
        type: 'positive',
        message: 'External URL saved',
        timeout: 1000
      })
    },

    async getPricePerMessage() {
      try {
        const {data} = await LNbits.api.request(
          'GET',
          '/bitsatcredit/api/v1/settings/price',
          null
        )
        this.pricePerMessage = data.price_per_message_sats
      } catch (error) {
        console.error('Error fetching price:', error)
        this.pricePerMessage = 1
      }
    },

    async savePriceSetting() {
      try {
        if (this.pricePerMessage < 1) {
          Quasar.Notify.create({
            type: 'warning',
            message: 'Price must be at least 1 sat',
            timeout: 2000
          })
          this.pricePerMessage = 1
          return
        }

        const {data} = await LNbits.api.request(
          'POST',
          `/bitsatcredit/api/v1/admin/settings/price?price_sats=${this.pricePerMessage}`,
          this.g.user.wallets[0].adminkey
        )

        Quasar.Notify.create({
          type: 'positive',
          message: `Price updated to ${data.price_per_message_sats} sat per message`,
          timeout: 2000
        })
      } catch (error) {
        LNbits.utils.notifyApiError(error)
      }
    },

    async getSystemStatus() {
      try {
        const {data} = await LNbits.api.request(
          'GET',
          '/bitsatcredit/api/v1/system/status',
          null
        )
        this.systemStatus = data.status
        this.systemOnline = data.is_online
        this.systemStatusMessage = data.message || ''
      } catch (error) {
        console.error('Error fetching system status:', error)
      }
    },

    async toggleSystemStatus(newValue) {
      try {
        const newStatus = newValue ? 'online' : 'offline'

        const {data} = await LNbits.api.request(
          'POST',
          `/bitsatcredit/api/v1/admin/system/status?status=${newStatus}&message=${encodeURIComponent(this.systemStatusMessage || '')}`,
          this.g.user.wallets[0].adminkey
        )

        this.systemStatus = data.status
        this.systemOnline = data.is_online
        this.systemStatusMessage = data.message || ''

        Quasar.Notify.create({
          type: data.is_online ? 'positive' : 'warning',
          message: `System is now ${data.is_online ? 'ONLINE' : 'OFFLINE'}`,
          timeout: 2000
        })
      } catch (error) {
        LNbits.utils.notifyApiError(error)
        this.systemOnline = !this.systemOnline
      }
    },

    async saveStatusMessage() {
      if (this.systemStatus === 'offline') {
        await this.toggleSystemStatus()
      }
    },

    //////////////// Admin Actions ////////////////////////
    showAddCreditsDialog() {
      this.addCreditsDialog = {
        show: true,
        npub: '',
        amount: null,
        memo: 'Admin credit addition'
      }
    },

    async addCreditsToUser() {
      try {
        const {data} = await LNbits.api.request(
          'POST',
          `/bitsatcredit/api/v1/admin/add-credits`,
          this.g.user.wallets[0].adminkey,
          {
            npub: this.addCreditsDialog.npub,
            amount: this.addCreditsDialog.amount,
            memo: this.addCreditsDialog.memo || 'Admin credit addition'
          }
        )

        Quasar.Notify.create({
          type: 'positive',
          message: `Added ${this.addCreditsDialog.amount} sats to user`,
          timeout: 2000
        })

        this.addCreditsDialog.show = false
        await this.getUsers()
        await this.getStats()
      } catch (error) {
        LNbits.utils.notifyApiError(error)
      }
    },

    showCreateUserDialog() {
      this.createUserDialog = {
        show: true,
        npub: '',
        initialBalance: 100
      }
    },

    async createNewUser() {
      try {
        const {data: user} = await LNbits.api.request(
          'GET',
          `/bitsatcredit/api/v1/user/${this.createUserDialog.npub}`,
          null
        )

        if (this.createUserDialog.initialBalance > 0) {
          await LNbits.api.request(
            'POST',
            `/bitsatcredit/api/v1/admin/add-credits`,
            this.g.user.wallets[0].adminkey,
            {
              npub: this.createUserDialog.npub,
              amount: this.createUserDialog.initialBalance,
              memo: 'Initial balance'
            }
          )
        }

        Quasar.Notify.create({
          type: 'positive',
          message: 'User created successfully',
          timeout: 2000
        })

        this.createUserDialog.show = false
        await this.getUsers()
        await this.getStats()
      } catch (error) {
        LNbits.utils.notifyApiError(error)
      }
    },

    editUserBalance() {
      if (this.userDetailsDialog.user) {
        this.editBalanceDialog = {
          show: true,
          npub: this.userDetailsDialog.user.npub,
          currentBalance: this.userDetailsDialog.user.balance_sats,
          newBalance: this.userDetailsDialog.user.balance_sats,
          memo: ''
        }
        this.userDetailsDialog.show = false
      }
    },

    async updateUserBalance() {
      try {
        const difference = this.editBalanceDialog.newBalance - this.editBalanceDialog.currentBalance

        if (difference === 0) {
          Quasar.Notify.create({
            type: 'warning',
            message: 'No change in balance',
            timeout: 1000
          })
          this.editBalanceDialog.show = false
          return
        }

        await LNbits.api.request(
          'POST',
          `/bitsatcredit/api/v1/admin/add-credits`,
          this.g.user.wallets[0].adminkey,
          {
            npub: this.editBalanceDialog.npub,
            amount: difference,
            memo: this.editBalanceDialog.memo || `Balance adjustment: ${this.editBalanceDialog.currentBalance} -> ${this.editBalanceDialog.newBalance}`
          }
        )

        Quasar.Notify.create({
          type: 'positive',
          message: 'Balance updated successfully',
          timeout: 2000
        })

        this.editBalanceDialog.show = false
        await this.getUsers()
        await this.getStats()
      } catch (error) {
        LNbits.utils.notifyApiError(error)
      }
    },

    editUserMemo(user) {
      this.editMemoDialog = {
        show: true,
        npub: user.npub,
        memo: user.memo || ''
      }
    },

    async saveUserMemo() {
      try {
        const {data} = await LNbits.api.request(
          'POST',
          `/bitsatcredit/api/v1/admin/user/${this.editMemoDialog.npub}/memo?memo=${encodeURIComponent(this.editMemoDialog.memo)}`,
          this.g.user.wallets[0].adminkey
        )

        Quasar.Notify.create({
          type: 'positive',
          message: 'Memo updated successfully',
          timeout: 2000
        })

        this.editMemoDialog.show = false
        await this.getUsers()
      } catch (error) {
        LNbits.utils.notifyApiError(error)
      }
    },

    showBulkAddCreditsDialog() {
      this.bulkAddCreditsDialog = {
        show: true,
        amount: null,
        memo: 'Bulk credit addition'
      }
    },

    async bulkAddCreditsToUsers() {
      try {
        let successCount = 0
        let failCount = 0

        for (const npub of this.selectedUsers) {
          try {
            await LNbits.api.request(
              'POST',
              `/bitsatcredit/api/v1/admin/add-credits`,
              this.g.user.wallets[0].adminkey,
              {
                npub: npub,
                amount: this.bulkAddCreditsDialog.amount,
                memo: this.bulkAddCreditsDialog.memo || 'Bulk credit addition'
              }
            )
            successCount++
          } catch (error) {
            console.error(`Failed to add credits to ${npub}:`, error)
            failCount++
          }
        }

        Quasar.Notify.create({
          type: 'positive',
          message: `Added ${this.bulkAddCreditsDialog.amount} sats to ${successCount} user(s)${failCount > 0 ? `, ${failCount} failed` : ''}`,
          timeout: 3000
        })

        this.bulkAddCreditsDialog.show = false
        this.selectedUsers = []
        this.selectAll = false
        await this.getUsers()
        await this.getStats()
      } catch (error) {
        LNbits.utils.notifyApiError(error)
      }
    },

    confirmDeleteUser() {
      if (!this.userDetailsDialog.user) return

      const npub = this.userDetailsDialog.user.npub

      Quasar.Dialog.create({
        title: 'Confirm Delete',
        message: `Are you sure you want to delete user ${npub.substring(0, 16)}...? This will delete all transactions and top-up records. This action cannot be undone.`,
        cancel: true,
        persistent: true
      }).onOk(async () => {
        await this.deleteUser(npub)
      })
    },

    async deleteUser(npub) {
      try {
        await LNbits.api.request(
          'DELETE',
          `/bitsatcredit/api/v1/admin/user/${npub}`,
          this.g.user.wallets[0].adminkey
        )

        Quasar.Notify.create({
          type: 'positive',
          message: 'User deleted successfully',
          timeout: 2000
        })

        this.userDetailsDialog.show = false
        await this.getUsers()
        await this.getStats()
        await this.getRecentTransactions()
      } catch (error) {
        LNbits.utils.notifyApiError(error)
      }
    }
  },

  ///////////////////////////////////////////////////
  //////LIFECYCLE FUNCTIONS RUNNING ON PAGE LOAD/////
  ///////////////////////////////////////////////////
  async created() {
    await this.getStats()
    await this.getUsers()
    await this.getRecentTransactions()
    await this.getSystemStatus()
    await this.getPricePerMessage()

    this.loadWalletOptions()
    const savedWalletId = localStorage.getItem('bitsatcredit_wallet_id')
    if (savedWalletId) {
      this.selectedWallet = this.walletOptions.find(w => w.value === savedWalletId) || this.walletOptions[0]
    }

    this.externalUrl = localStorage.getItem('bitsatcredit_external_url') || ''
  }
})
