// src/utils/currentDataManager.js
import { watch } from 'vue';

export class CurrentDataManager {
  constructor(ws, auth) {
    this.ws = ws;
    this.auth = auth;
    this.subscribers = new Map();
    this.edgeSet = new Set();
    this.channelSet = new Set();
    this.isSubscribed = false;
    this.reconnectAttempts = 0;
    this.maxReconnectAttempts = 5;
    
    this._handleMessage = this._handleMessage.bind(this);
    this._handleOpen = this._handleOpen.bind(this);
    this._handleClose = this._handleClose.bind(this);
    this._handleError = this._handleError.bind(this);

    this._initialize();
  }

  _initialize() {
    if (!this.ws) return;
    
    // Add all WebSocket event listeners
    this.ws.addEventListener('message', this._handleMessage);
    this.ws.addEventListener('open', this._handleOpen);
    this.ws.addEventListener('close', this._handleClose);
    this.ws.addEventListener('error', this._handleError);

    // Watch for auth changes
    if (this.auth) {
      watch(() => this.auth.ready, (ready) => {
        console.debug('[CurrentDataManager] Auth ready:', ready);
        if (ready) {
          this._attemptSubscription();
        }
      }, { immediate: true });
    }

    // If WebSocket is already open, attempt subscription
    if (this.ws.readyState === WebSocket.OPEN) {
      this._attemptSubscription();
    }
  }

  register(id, edges, channels, callback) {
    console.debug('[CurrentDataManager] Registering subscriber:', id);
    this.subscribers.set(id, { edges, channels, callback });
    this._updateSets();
    this._attemptSubscription();
  }

  unregister(id) {
    console.debug('[CurrentDataManager] Unregistering subscriber:', id);
    this.subscribers.delete(id);
    this._updateSets();
    
    // If no more subscribers, we could optionally unsubscribe
    if (this.subscribers.size === 0) {
      this.isSubscribed = false;
    }
  }

  _updateSets() {
    this.edgeSet = new Set();
    this.channelSet = new Set();

    for (const { edges, channels } of this.subscribers.values()) {
      edges.forEach(e => this.edgeSet.add(e));
      channels.forEach(c => this.channelSet.add(c));
    }
  }

  _handleOpen() {
    console.debug('[CurrentDataManager] WebSocket opened');
    this.reconnectAttempts = 0;
    this._attemptSubscription();
  }

  _handleClose(event) {
    console.debug('[CurrentDataManager] WebSocket closed:', event.code, event.reason);
    this.isSubscribed = false;
    
    // Attempt to reconnect if not a clean close
    if (event.code !== 1000 && this.reconnectAttempts < this.maxReconnectAttempts) {
      this.reconnectAttempts++;
      console.debug(`[CurrentDataManager] Attempting reconnect ${this.reconnectAttempts}/${this.maxReconnectAttempts}`);
      setTimeout(() => this._attemptSubscription(), 2000 * this.reconnectAttempts);
    }
  }

  _handleError(error) {
    console.error('[CurrentDataManager] WebSocket error:', error);
  }

  async _attemptSubscription() {
    // Check all prerequisites
    if (!this.ws || 
        this.ws.readyState !== WebSocket.OPEN || 
        !this.auth?.ready || 
        this.isSubscribed ||
        this.edgeSet.size === 0 || 
        this.channelSet.size === 0) {
      return;
    }

    try {
      await this._subscribeAll();
      // Request initial data after subscription
      await this._requestInitialData();
    } catch (error) {
      console.error('[CurrentDataManager] Subscription failed:', error);
    }
  }

  async _subscribeAll() {
    const edges = Array.from(this.edgeSet);
    const channels = Array.from(this.channelSet);

    console.debug('[CurrentDataManager] Subscribing to edges:', edges, 'channels:', channels);

    console.debug('waaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa');
    // Subscribe to edges first
    const edgeSubscribePromise = this._sendMessage({
      jsonrpc: '2.0',
      id: crypto.randomUUID(),
      method: 'subscribeEdges',
      params: { edges }
    });

    // Subscribe to channels
    const channelSubscribePromise = this._sendMessage({
      jsonrpc: '2.0',
      id: crypto.randomUUID(),
      method: 'edgeRpc',
      params: {
        edgeId: edges[0],
        payload: {
          jsonrpc: '2.0',
          id: crypto.randomUUID(),
          method: 'subscribeChannels',
          params: { count: 0, ids: edges, channels }
        }
      }
    });

    await Promise.all([edgeSubscribePromise, channelSubscribePromise]);
    this.isSubscribed = true;
    console.debug('[CurrentDataManager] Successfully subscribed');
  }

  async _requestInitialData() {
    const edges = Array.from(this.edgeSet);
    const channels = Array.from(this.channelSet);

    // Request current data for all subscribed channels
    const requestId = crypto.randomUUID();
    
    return this._sendMessage({
      jsonrpc: '2.0',
      id: requestId,
      method: 'edgeRpc',
      params: {
        edgeId: edges[0],
        payload: {
          jsonrpc: '2.0',
          id: crypto.randomUUID(),
          method: 'getCurrentData', // This might be 'getChannelValues' or similar
          params: { ids: edges, channels }
        }
      }
    });
  }

  _sendMessage(message) {
    return new Promise((resolve, reject) => {
      if (this.ws.readyState !== WebSocket.OPEN) {
        reject(new Error('WebSocket not open'));
        return;
      }

      const messageId = message.id;
      const timeout = setTimeout(() => {
        reject(new Error('Message timeout'));
      }, 10000); // 10 second timeout

      // Listen for response (you might need to adjust this based on your API)
      const handleResponse = (event) => {
        try {
          const response = JSON.parse(event.data);
          if (response.id === messageId) {
            clearTimeout(timeout);
            this.ws.removeEventListener('message', handleResponse);
            if (response.error) {
              reject(new Error(response.error.message || 'Server error'));
            } else {
              resolve(response.result);
            }
          }
        } catch (e) {
          // Ignore parsing errors for other messages
        }
      };

      this.ws.addEventListener('message', handleResponse);
      this.ws.send(JSON.stringify(message));
    });
  }

  _handleMessage(event) {
    let msg;
    try { 
      msg = JSON.parse(event.data); 
    } catch (e) { 
      console.warn('[CurrentDataManager] Failed to parse message:', event.data);
      return; 
    }

    // Handle real-time data updates
    if (msg.method === 'edgeRpc' && 
        msg.params?.payload?.method === 'currentData') {
      
      const data = msg.params.payload.params;
      this._distributeData(data);
    }
    
    // Handle initial data response
    else if (msg.result && msg.id) {
      // This handles responses to getCurrentData requests
      this._distributeData(msg.result);
    }
  }

  _distributeData(data) {
    if (!data || typeof data !== 'object') return;

    console.debug('[CurrentDataManager] Distributing data:', data);
    
    // Distribute data to all subscribers
    for (const { channels, callback } of this.subscribers.values()) {
      const filtered = {};
      let hasData = false;
      
      channels.forEach(ch => {
        if (data[ch] != null) {
          filtered[ch] = data[ch];
          hasData = true;
        }
      });
      
      if (hasData) {
        try {
          callback(filtered);
        } catch (error) {
          console.error('[CurrentDataManager] Error in subscriber callback:', error);
        }
      }
    }
  }

  // Method to manually refresh data
  async refreshData() {
    if (this.isSubscribed) {
      await this._requestInitialData();
    }
  }

  destroy() {
    console.debug('[CurrentDataManager] Destroying manager');
    
    if (this.ws) {
      this.ws.removeEventListener('message', this._handleMessage);
      this.ws.removeEventListener('open', this._handleOpen);
      this.ws.removeEventListener('close', this._handleClose);
      this.ws.removeEventListener('error', this._handleError);
    }
    
    this.subscribers.clear();
    this.edgeSet.clear();
    this.channelSet.clear();
    this.isSubscribed = false;
  }
}