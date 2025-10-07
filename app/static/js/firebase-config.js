/**
 * Firebase Client SDK Configuration
 * Visioneer - AI-Powered Moodboard Creator
 */

// Firebase configuration from environment
const firebaseConfig = {
  apiKey: "AIzaSyBI4dkR8RJt3fCaUsqGgTKENPCD2WPKjeQ",
  authDomain: "visioneer-f1ff4.firebaseapp.com",
  projectId: "visioneer-f1ff4",
  storageBucket: "visioneer-f1ff4.firebasestorage.app",
  messagingSenderId: "867557307596",
  appId: "1:867557307596:web:d006945e36611dd8a93e69",
  measurementId: "G-1EBJMKN7PT"
};

// Initialize Firebase
const app = firebase.initializeApp(firebaseConfig);
const auth = firebase.auth();
const analytics = firebase.analytics();

// Configure Google Sign-In provider
const googleProvider = new firebase.auth.GoogleAuthProvider();
googleProvider.setCustomParameters({
  prompt: 'select_account'
});

/**
 * Register user with email and password
 */
async function registerWithEmail(email, password, displayName) {
  try {
    const userCredential = await auth.createUserWithEmailAndPassword(email, password);
    const user = userCredential.user;

    // Update user profile with display name
    await user.updateProfile({
      displayName: displayName
    });

    // Send email verification
    await user.sendEmailVerification();

    // Get ID token to send to backend
    const idToken = await user.getIdToken();

    return {
      success: true,
      user: user,
      idToken: idToken,
      message: 'Registration successful! Please check your email to verify your account.'
    };
  } catch (error) {
    return {
      success: false,
      error: error.code,
      message: getFirebaseErrorMessage(error)
    };
  }
}

/**
 * Sign in user with email and password
 */
async function signInWithEmail(email, password) {
  try {
    const userCredential = await auth.signInWithEmailAndPassword(email, password);
    const user = userCredential.user;

    // Get ID token to send to backend
    const idToken = await user.getIdToken();

    return {
      success: true,
      user: user,
      idToken: idToken
    };
  } catch (error) {
    return {
      success: false,
      error: error.code,
      message: getFirebaseErrorMessage(error)
    };
  }
}

/**
 * Sign in with Google
 */
async function signInWithGoogle() {
  try {
    const result = await auth.signInWithPopup(googleProvider);
    const user = result.user;

    // Get ID token to send to backend
    const idToken = await user.getIdToken();

    return {
      success: true,
      user: user,
      idToken: idToken
    };
  } catch (error) {
    return {
      success: false,
      error: error.code,
      message: getFirebaseErrorMessage(error)
    };
  }
}

/**
 * Send password reset email
 */
async function sendPasswordReset(email) {
  try {
    await auth.sendPasswordResetEmail(email);

    return {
      success: true,
      message: 'Password reset email sent! Please check your inbox.'
    };
  } catch (error) {
    return {
      success: false,
      error: error.code,
      message: getFirebaseErrorMessage(error)
    };
  }
}

/**
 * Sign out user
 */
async function signOutUser() {
  try {
    await auth.signOut();

    return {
      success: true,
      message: 'Logged out successfully'
    };
  } catch (error) {
    return {
      success: false,
      error: error.code,
      message: 'Failed to log out'
    };
  }
}

/**
 * Send ID token to backend for session creation
 */
async function sendTokenToBackend(idToken, endpoint = '/api/login') {
  try {
    const response = await fetch(endpoint, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ id_token: idToken })
    });

    const data = await response.json();

    if (response.ok) {
      return {
        success: true,
        data: data
      };
    } else {
      return {
        success: false,
        error: data.error || 'Authentication failed'
      };
    }
  } catch (error) {
    return {
      success: false,
      error: 'Network error. Please try again.'
    };
  }
}

/**
 * Get user-friendly error messages
 */
function getFirebaseErrorMessage(error) {
  const errorMessages = {
    'auth/email-already-in-use': 'This email address is already registered. Please sign in instead.',
    'auth/invalid-email': 'Please enter a valid email address.',
    'auth/operation-not-allowed': 'Email/password sign-in is not enabled. Please contact support.',
    'auth/weak-password': 'Password is too weak. Please use at least 6 characters.',
    'auth/user-disabled': 'This account has been disabled. Please contact support.',
    'auth/user-not-found': 'No account found with this email. Please register first.',
    'auth/wrong-password': 'Incorrect password. Please try again or reset your password.',
    'auth/too-many-requests': 'Too many failed attempts. Please try again later.',
    'auth/network-request-failed': 'Network error. Please check your connection and try again.',
    'auth/popup-closed-by-user': 'Sign-in cancelled. Please try again.',
    'auth/popup-blocked': 'Popup was blocked by your browser. Please allow popups for this site.',
    'auth/account-exists-with-different-credential': 'An account already exists with this email using a different sign-in method.',
    'auth/invalid-credential': 'Invalid credentials. Please try again.',
    'auth/requires-recent-login': 'This operation requires recent authentication. Please sign in again.'
  };

  return errorMessages[error.code] || error.message || 'An error occurred. Please try again.';
}

/**
 * Display error message to user
 */
function showError(message) {
  const errorDiv = document.getElementById('auth-error');
  if (errorDiv) {
    errorDiv.textContent = message;
    errorDiv.classList.remove('hidden');

    // Auto-hide after 5 seconds
    setTimeout(() => {
      errorDiv.classList.add('hidden');
    }, 5000);
  }
}

/**
 * Display success message to user
 */
function showSuccess(message) {
  const successDiv = document.getElementById('auth-success');
  if (successDiv) {
    successDiv.textContent = message;
    successDiv.classList.remove('hidden');

    // Auto-hide after 5 seconds
    setTimeout(() => {
      successDiv.classList.add('hidden');
    }, 5000);
  }
}

/**
 * Show loading state
 */
function setLoading(isLoading, button) {
  if (button) {
    button.disabled = isLoading;
    const buttonText = button.querySelector('.button-text');
    const buttonLoader = button.querySelector('.button-loader');

    if (buttonText && buttonLoader) {
      if (isLoading) {
        buttonText.classList.add('hidden');
        buttonLoader.classList.remove('hidden');
      } else {
        buttonText.classList.remove('hidden');
        buttonLoader.classList.add('hidden');
      }
    }
  }
}
