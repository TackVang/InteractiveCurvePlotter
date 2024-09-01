<template>
  <div id="app">
    <h1>Server Simulation Command Executor</h1>

    <div v-if="error" class="error">
      {{ error }}
    </div>

    <div v-if="successMessage" class="success">
      {{ successMessage }}
    </div>

    <div>
      <label for="command">Simulation Command:</label>
      <input type="text" v-model="command" id="command" required>
      <button @click="executeCommand">Execute on Least Loaded Server</button>
    </div>
  </div>
</template>

<script>
import axios from 'axios';

export default {
  data() {
    return {
      command: '',
      error: null,
      successMessage: null
    }
  },
  methods: {
    async executeCommand() {
      this.error = null;
      this.successMessage = null;

      try {
        // 最も稼働率が低いサーバーを取得
        const response = await axios.get('http://127.0.0.1:5000/get-least-loaded-server');
        const server = response.data;

        // コマンドを実行
        const executeResponse = await axios.post('http://127.0.0.1:5000/execute-command', {
          command: this.command,
          server: server
        });

        this.successMessage = executeResponse.data.output;
      } catch (err) {
        this.error = err.response ? err.response.data.error : 'An error occurred.';
      }
    }
  }
}
</script>

<style>
#app {
  font-family: Avenir, Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  text-align: center;
  color: #2c3e50;
  margin-top: 60px;
}
.error {
  color: red;
  margin-bottom: 10px;
}
.success {
  color: green;
  margin-bottom: 10px;
}
</style>
