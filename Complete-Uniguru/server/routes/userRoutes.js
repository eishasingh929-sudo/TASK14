import express from 'express';
import {
  signup,
  login,
  getAuthStatus,
  logout,
  updateUser,
  updatePassword,
  deleteUser
} from '../controller/userController.js';
import {
  forgotPassword,
  resetPassword
} from '../controller/authController.js';
import { protect, optionalAuth } from '../middleware/auth.js';
import {
  validateUserRegistration,
  validateUserLogin
} from '../middleware/validation.js';

const router = express.Router();

// Public routes
router.post('/signup', validateUserRegistration, signup);
router.post('/login', validateUserLogin, login);
router.post('/forgot-password', forgotPassword);
router.put('/reset-password/:resettoken', resetPassword);

// Protected routes
router.get('/auth-status', optionalAuth, getAuthStatus);
router.get('/logout', protect, logout);
router.put('/update', protect, updateUser);
router.put('/password', protect, updatePassword);
router.delete('/delete', protect, deleteUser);

export default router;
