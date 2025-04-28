// analysis-result.model.js
const analysisResultSchema = new mongoose.Schema({
    testCaseId: { type: String, required: true, unique: true },
    objective: String,
    status: String,
    commitDetails: {
      startTime: Date,
      endTime: Date,
      duration: String,
      commits: [{
        hash: String,
        message: String,
        date: Date,
        author: String,
        codeChanges: Map
      }]
    },
    
    llmAnalysis: {
      summary_of_change: [String],
      code_complexity: Map,
      code_quality: Map,
      code_readability: Map,
      skills_gained: [String],
      recommendations: [String],
      code_review: String,
      estimated_time: Map,
      developer_performance: Map,
      languages_used: String
    },
    lastUpdated: Date,
    created: { type: Date, default: Date.now }
  });