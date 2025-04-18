module.exports = {
  onPreBuild: async ({ utils }) => {
    console.log('Setting npm config to ignore engine requirements');
    try {
      await utils.run.command('npm config set engine-strict false');
      console.log('Successfully disabled strict engine checking');
    } catch (error) {
      console.error('Error setting npm config:', error);
    }
  }
};