import mongoose from 'mongoose';

const guruSchema = new mongoose.Schema({
  name: {
    type: String,
    required: [true, 'Please provide a guru name'],
    trim: true,
    maxlength: [100, 'Guru name cannot be more than 100 characters']
  },
  description: {
    type: String,
    trim: true,
    maxlength: [500, 'Description cannot be more than 500 characters'],
    default: ''
  },
  subject: {
    type: String,
    required: [true, 'Please provide a subject/expertise'],
    trim: true,
    maxlength: [100, 'Subject cannot be more than 100 characters']
  },
  user: {
    type: mongoose.Schema.ObjectId,
    ref: 'User',
    required: [true, 'Guru must belong to a user']
  },
  systemPrompt: {
    type: String,
    default: function() {
      return `You are ${this.name}, an expert in ${this.subject}. ${this.description ? this.description + ' ' : ''}You are helpful, knowledgeable, and passionate about teaching. Always provide accurate, detailed explanations and encourage learning. Maintain a friendly and professional tone while staying true to your expertise in ${this.subject}.`;
    }
  },
  avatar: {
    type: String,
    default: null
  },
  isActive: {
    type: Boolean,
    default: true
  },
  settings: {
    model: {
      type: String,
      enum: ['llama3.1'],
      default: 'llama3.1'
    },
    temperature: {
      type: Number,
      min: 0,
      max: 2,
      default: 0.7
    },
    maxTokens: {
      type: Number,
      min: 1,
      max: 4096,
      default: 1024
    },
    topP: {
      type: Number,
      min: 0,
      max: 1,
      default: 1
    }
  },
  stats: {
    totalChats: {
      type: Number,
      default: 0
    },
    totalMessages: {
      type: Number,
      default: 0
    },
    lastUsed: {
      type: Date,
      default: null
    }
  },
  tags: [{
    type: String,
    trim: true,
    maxlength: [30, 'Tag cannot be more than 30 characters']
  }],
  isPublic: {
    type: Boolean,
    default: false
  },
  likes: {
    type: Number,
    default: 0
  },
  likedBy: [{
    type: mongoose.Schema.ObjectId,
    ref: 'User'
  }]
}, {
  timestamps: true,
  toJSON: { virtuals: true },
  toObject: { virtuals: true }
});

// Virtual for guru's chats
guruSchema.virtual('chats', {
  ref: 'Chat',
  localField: '_id',
  foreignField: 'guru',
  justOne: false
});

// Update system prompt when name, subject, or description changes
guruSchema.pre('save', function(next) {
  if (this.isModified('name') || this.isModified('subject') || this.isModified('description')) {
    this.systemPrompt = `You are ${this.name}, an expert in ${this.subject}. ${this.description ? this.description + ' ' : ''}You are helpful, knowledgeable, and passionate about teaching. Always provide accurate, detailed explanations and encourage learning. Maintain a friendly and professional tone while staying true to your expertise in ${this.subject}.`;
  }
  next();
});

// Update stats when guru is used
guruSchema.methods.updateStats = function(incrementMessages = false) {
  this.stats.lastUsed = Date.now();
  if (incrementMessages) {
    this.stats.totalMessages += 1;
  }
  return this.save({ validateBeforeSave: false });
};

// Method to increment chat count
guruSchema.methods.incrementChatCount = function() {
  this.stats.totalChats += 1;
  return this.save({ validateBeforeSave: false });
};

// Method to like/unlike guru
guruSchema.methods.toggleLike = function(userId) {
  const userIndex = this.likedBy.indexOf(userId);
  if (userIndex > -1) {
    // Unlike
    this.likedBy.splice(userIndex, 1);
    this.likes = Math.max(0, this.likes - 1);
  } else {
    // Like
    this.likedBy.push(userId);
    this.likes += 1;
  }
  return this.save({ validateBeforeSave: false });
};

// Create indexes
guruSchema.index({ user: 1 });
guruSchema.index({ subject: 1 });
guruSchema.index({ isPublic: 1, likes: -1 });
guruSchema.index({ createdAt: -1 });
guruSchema.index({ 'stats.lastUsed': -1 });

export default mongoose.model('Guru', guruSchema);
