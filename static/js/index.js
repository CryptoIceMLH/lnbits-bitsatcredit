window.app = Vue.createApp({
  el: '#vue',
  mixins: [windowMixin],
  delimiters: ['${', '}'],
  data: function () {
    return {
      currencyOptions: ['sat'],
      settingsFormDialog: {
        show: false,
        data: {}
      },

      serverFormDialog: {
        show: false,
        data: {
          wallet: null,
          credit: null,
          
        }
      },
      serverList: [],
      serverTable: {
        search: '',
        loading: false,
        columns: [
          {"name": "name_id", "align": "left", "label": "Name", "field": "name_id", "sortable": true},
          {"name": "description_id", "align": "left", "label": "Description", "field": "description_id", "sortable": true},
          {"name": "wallet", "align": "left", "label": "Wallet", "field": "wallet", "sortable": true},
          {"name": "credit", "align": "left", "label": "Credit", "field": "credit", "sortable": true},
          {"name": "updated_at", "align": "left", "label": "Updated At", "field": "updated_at", "sortable": true},
          {"name": "id", "align": "left", "label": "ID", "field": "id", "sortable": true},
          
        ],
        pagination: {
          sortBy: 'updated_at',
          rowsPerPage: 10,
          page: 1,
          descending: true,
          rowsNumber: 10
        }
      },

      relayFormDialog: {
        show: false,
        server: {label: 'All Server', value: ''},
        data: {}
      },
      relayList: [],
      relayTable: {
        search: '',
        loading: false,
        columns: [
          {"name": "npub", "align": "left", "label": "Npub", "field": "npub", "sortable": true},
          {"name": "sats", "align": "left", "label": "Sats", "field": "sats", "sortable": true},
          {"name": "paid", "align": "left", "label": "Paid", "field": "paid", "sortable": true},
          {"name": "updated_at", "align": "left", "label": "Updated At", "field": "updated_at", "sortable": true},
          {"name": "id", "align": "left", "label": "ID", "field": "id", "sortable": true},
          
        ],
        pagination: {
          sortBy: 'updated_at',
          rowsPerPage: 10,
          page: 1,
          descending: true,
          rowsNumber: 10
        }
      }
    }
  },
  watch: {
    'serverTable.search': {
      handler() {
        const props = {}
        if (this.serverTable.search) {
          props['search'] = this.serverTable.search
        }
        this.getServer()
      }
    },
    'relayTable.search': {
      handler() {
        const props = {}
        if (this.relayTable.search) {
          props['search'] = this.relayTable.search
        }
        this.getRelay()
      }
    },
    'relayFormDialog.server.value': {
      handler() {
        const props = {}
        if (this.relayTable.search) {
          props['search'] = this.relayTable.search
        }
        this.getRelay()
      }
    }
  },

  methods: {

    //////////////// Server ////////////////////////
    async showNewServerForm() {
      this.serverFormDialog.data = {
          wallet: null,
          credit: null,
          
      }
      this.serverFormDialog.show = true
    },
    async showEditServerForm(data) {
      this.serverFormDialog.data = {...data}
      this.serverFormDialog.show = true
    },
    async saveServer() {
      
      try {
        const data = {extra: {}, ...this.serverFormDialog.data}
        const method = data.id ? 'PUT' : 'POST'
        const entry = data.id ? `/${data.id}` : ''
        await LNbits.api.request(
          method,
          '/bitsatcredit/api/v1/server' + entry,
          null,
          data
        )
        this.getServer()
        this.serverFormDialog.show = false
      } catch (error) {
        LNbits.utils.notifyApiError(error)
      }
    },

    async getServer(props) {
      
      try {
        this.serverTable.loading = true
        const params = LNbits.utils.prepareFilterQuery(
          this.serverTable,
          props
        )
        const {data} = await LNbits.api.request(
          'GET',
          `/bitsatcredit/api/v1/server/paginated?${params}`,
          null
        )
        this.serverList = data.data
        this.serverTable.pagination.rowsNumber = data.total
      } catch (error) {
        LNbits.utils.notifyApiError(error)
      } finally {
        this.serverTable.loading = false
      }
    },
    async deleteServer(serverId) {
      await LNbits.utils
        .confirmDialog('Are you sure you want to delete this Server?')
        .onOk(async () => {
          try {
            
            await LNbits.api.request(
              'DELETE',
              '/bitsatcredit/api/v1/server/' + serverId,
              null
            )
            await this.getServer()
          } catch (error) {
            LNbits.utils.notifyApiError(error)
          }
        })
    },
    async exportServerCSV() {
      await LNbits.utils.exportCSV(
        this.serverTable.columns,
        this.serverList,
        'server_' + new Date().toISOString().slice(0, 10) + '.csv'
      )
    },

    //////////////// Relay ////////////////////////
    async showEditRelayForm(data) {
      this.relayFormDialog.data = {...data}
      this.relayFormDialog.show = true
    },
    async saveRelay() {
      
      try {
        const data = {extra: {}, ...this.relayFormDialog.data}
        const method = data.id ? 'PUT' : 'POST'
        const entry = data.id ? `/${data.id}` : ''
        await LNbits.api.request(
          method,
          '/bitsatcredit/api/v1/relay' + entry,
          null,
          data
        )
        this.getRelay()
        this.relayFormDialog.show = false
      } catch (error) {
        LNbits.utils.notifyApiError(error)
      }
    },

    async getRelay(props) {
      
      try {
        this.relayTable.loading = true
        let params = LNbits.utils.prepareFilterQuery(
          this.relayTable,
          props
        )
        const serverId = this.relayFormDialog.server.value
        if (serverId) {
          params += `&server_id=${serverId}`
        }
        const {data} = await LNbits.api.request(
          'GET',
          `/bitsatcredit/api/v1/relay/paginated?${params}`,
          null
        )
        this.relayList = data.data
        this.relayTable.pagination.rowsNumber = data.total
      } catch (error) {
        LNbits.utils.notifyApiError(error)
      } finally {
        this.relayTable.loading = false
      }
    },
    async deleteRelay(relayId) {
      await LNbits.utils
        .confirmDialog('Are you sure you want to delete this Relay?')
        .onOk(async () => {
          try {
            
            await LNbits.api.request(
              'DELETE',
              '/bitsatcredit/api/v1/relay/' + relayId,
              null
            )
            await this.getRelay()
          } catch (error) {
            LNbits.utils.notifyApiError(error)
          }
        })
    },

    async exportRelayCSV() {
      await LNbits.utils.exportCSV(
        this.relayTable.columns,
        this.relayList,
        'relay_' + new Date().toISOString().slice(0, 10) + '.csv'
      )
    },

    //////////////// Utils ////////////////////////
    dateFromNow(date) {
      return moment(date).fromNow()
    },
    async fetchCurrencies() {
      try {
        const response = await LNbits.api.request('GET', '/api/v1/currencies')
        this.currencyOptions = ['sat', ...response.data]
      } catch (error) {
        LNbits.utils.notifyApiError(error)
      }
    }
  },
  ///////////////////////////////////////////////////
  //////LIFECYCLE FUNCTIONS RUNNING ON PAGE LOAD/////
  ///////////////////////////////////////////////////
  async created() {
    this.fetchCurrencies()
    this.getServer()
    this.getRelay()

    
    
  }
})