import ToolAnalytics from '../tools/tool-analytics.js';

console.log('Testing CLI components...');

try {
  const analytics = new ToolAnalytics();
  const data = analytics.loadData();

  if (data) {
    console.log(`✅ Data loaded: ${data.totalCalls} total calls`);

    const report = analytics.generateReport({
      timeframe: 'session',
      format: 'text'
    });

    console.log('\n📊 Sample Report:');
    console.log(report.substring(0, 500) + '...');
  } else {
    console.log('❌ No data found');
  }
} catch (error) {
  console.error('❌ Error:', error.message);
  console.error(error.stack);
}