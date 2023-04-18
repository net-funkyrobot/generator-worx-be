import { before, beforeEach, after } from 'mocha'
import { readFileSync } from 'fs'
import * as firebase from '@firebase/rules-unit-testing'

const PROJECT_ID = 'net-funkyrobot-blox-firestore-rules-testing'

function getAdminFirestore() {
  return firebase.initializeAdminApp({ projectId: PROJECT_ID }).firestore()
}

function getAuthedFirestore(auth) {
  return firebase
    .initializeTestApp({ projectId: PROJECT_ID, auth: auth })
    .firestore()
}

before(async () => {
  // Load firestore rules before running tests
  const rules = readFileSync('firestore.rules', 'utf-8')
  await firebase.loadFirestoreRules({ projectId: PROJECT_ID, rules: rules })
})

beforeEach(async () => {
  // Clear firestore data between tests
  await firebase.clearFirestoreData({ projectId: PROJECT_ID })
})

after(async () => {
  // Clear firestore data between tests
  await firebase.clearFirestoreData({ projectId: PROJECT_ID })

  // Delete all the FirebaseApp instances created during testing
  await Promise.all(firebase.apps().map((app) => app.delete()))
})

describe('Firestore rules', async () => {
  describe('for a user inside the users collection', async () => {
    const uid = 'normal-user'
    const otherUid = 'another-normal-user'

    it('ensures can create their user document', async () => {
      // Ensure can create their user doc
      const db = getAuthedFirestore({ uid: uid }) // Authenticated, not superadmin
      const userDoc = db.collection('users').doc(uid)
      await firebase.assertSucceeds(userDoc.set({ foo: 'bar' }))
    })

    it('ensures can read their user document', async () => {
      const adminDb = getAdminFirestore()
      const adminUserDoc = adminDb.collection('users').doc(uid)
      await adminUserDoc.set({ foo: 'bar' })

      // Ensure can read their user doc
      const db = getAuthedFirestore({ uid: uid }) // Authenticated, not superadmin
      const userDoc = db.collection('users').doc(uid)
      await firebase.assertSucceeds(userDoc.get())
    })

    it('ensures can update their user document', async () => {
      const adminDb = getAdminFirestore()
      const adminUserDoc = adminDb.collection('users').doc(uid)
      await adminUserDoc.set({ foo: 'bar' })

      // Ensure can update their user doc
      const db = getAuthedFirestore({ uid: uid }) // Authenticated, not superadmin
      const userDoc = db.collection('users').doc(uid)
      await firebase.assertSucceeds(userDoc.update({ foo: 'baz' }))
    })

    it('ensures cannot delete their user document', async () => {
      const adminDb = getAdminFirestore()
      const adminUserDoc = adminDb.collection('users').doc(uid)
      await adminUserDoc.set({ foo: 'bar' })

      // Ensure CANNOT delete their user document
      const db = getAuthedFirestore({ uid: uid }) // Authenticated, not superadmin
      const userDoc = db.collection('users').doc(uid)
      await firebase.assertFails(userDoc.delete())
    })

    it('ensures can create documents in subcollections belonging to their user', async () => {
      // Ensure can create a doc in a subcollection
      const db = getAuthedFirestore({ uid: uid }) // Authenticated, not superadmin
      const userSubcolDoc = db
        .collection('users')
        .doc(uid)
        .collection('foo')
        .doc('bar')
      await firebase.assertSucceeds(userSubcolDoc.set({ foo: 'bar' }))
    })

    it('ensures can read documents in subcollections belonging to their user', async () => {
      const adminDb = getAdminFirestore()
      const adminUserDoc = adminDb
        .collection('users')
        .doc(uid)
        .collection('foo')
        .doc('bar')
      await adminUserDoc.set({ foo: 'bar' })

      // Ensure user can read subcollection doc
      const db = getAuthedFirestore({ uid: uid }) // Authenticated, not superadmin
      const userSubcolDoc = db
        .collection('users')
        .doc(uid)
        .collection('foo')
        .doc('bar')
      await firebase.assertSucceeds(userSubcolDoc.get())
    })

    it('ensures can update documents in subcollections belonging to their user', async () => {
      const adminDb = getAdminFirestore()
      const adminUserDoc = adminDb
        .collection('users')
        .doc(uid)
        .collection('foo')
        .doc('bar')
      await adminUserDoc.set({ foo: 'bar' })

      // Ensure user can update subcollection doc
      const db = getAuthedFirestore({ uid: uid }) // Authenticated, not superadmin
      const userSubcolDoc = db
        .collection('users')
        .doc(uid)
        .collection('foo')
        .doc('bar')
      await firebase.assertSucceeds(userSubcolDoc.update({ foo: 'baz' }))
    })

    it('ensures cannot delete documents in subcollections belonging to their user', async () => {
      const adminDb = getAdminFirestore()
      const adminUserDoc = adminDb
        .collection('users')
        .doc(uid)
        .collection('foo')
        .doc('bar')
      await adminUserDoc.set({ foo: 'bar' })

      // Ensure user can delete subcollection doc
      const db = getAuthedFirestore({ uid: uid }) // Authenticated, not superadmin
      const userSubcolDoc = db
        .collection('users')
        .doc(uid)
        .collection('foo')
        .doc('bar')
      await firebase.assertSucceeds(userSubcolDoc.delete())
    })

    it('ensure cannot create other user documents', async () => {
      // Ensure cannot create user doc for other people
      const db = getAuthedFirestore({ uid: uid }) // Authenticated, not superadmin
      const userDoc = db.collection('users').doc(otherUid)
      await firebase.assertFails(userDoc.set({ foo: 'bar' }))
    })

    it('ensure cannot read other user documents', async () => {
      const adminDb = getAdminFirestore()
      const adminUserDoc = adminDb.collection('users').doc(otherUid)
      await adminUserDoc.set({ foo: 'bar' })

      // Ensure cannot read other user's user doc
      const db = getAuthedFirestore({ uid: uid }) // Authenticated, not superadmin
      const userDoc = db.collection('users').doc(otherUid)
      await firebase.assertFails(userDoc.get())
    })

    it('ensure cannot update other user documents', async () => {
      const adminDb = getAdminFirestore()
      const adminUserDoc = adminDb.collection('users').doc(otherUid)
      await adminUserDoc.set({ foo: 'bar' })

      // Ensure cannot update other user's user doc
      const db = getAuthedFirestore({ uid: uid }) // Authenticated, not superadmin
      const userDoc = db.collection('users').doc(otherUid)
      await firebase.assertFails(userDoc.update({ foo: 'baz' }))
    })

    it('ensure cannot delete other user documents', async () => {
      const adminDb = getAdminFirestore()
      const adminUserDoc = adminDb.collection('users').doc(otherUid)
      await adminUserDoc.set({ foo: 'bar' })

      // Ensure cannot delete other user's user doc
      const db = getAuthedFirestore({ uid: uid }) // Authenticated, not superadmin
      const userDoc = db.collection('users').doc(otherUid)
      await firebase.assertFails(userDoc.delete())
    })

    it('ensure cannot create documents in subcollections belonging to another user', async () => {
      // Ensure cannot create a doc in another user's subcollection
      const db = getAuthedFirestore({ uid: uid }) // Authenticated, not superadmin
      const otherUserSubcolDoc = db
        .collection('users')
        .doc(otherUid)
        .collection('foo')
        .doc('bar')
      await firebase.assertFails(otherUserSubcolDoc.set({ foo: 'bar' }))
    })

    it('ensure cannot read documents in subcollections belonging to another user', async () => {
      const adminDb = getAdminFirestore()
      const adminUserDoc = adminDb
        .collection('users')
        .doc(otherUid)
        .collection('foo')
        .doc('bar')
      await adminUserDoc.set({ foo: 'bar' })

      // Ensure user cannot read other users subcollection doc
      const db = getAuthedFirestore({ uid: uid }) // Authenticated, not superadmin
      const otherUserSubcolDoc = db
        .collection('users')
        .doc(otherUid)
        .collection('foo')
        .doc('bar')
      await firebase.assertFails(otherUserSubcolDoc.get())
    })

    it('ensure cannot update documents in subcollections belonging to another user', async () => {
      const adminDb = getAdminFirestore()
      const adminUserDoc = adminDb
        .collection('users')
        .doc(otherUid)
        .collection('foo')
        .doc('bar')
      await adminUserDoc.set({ foo: 'bar' })

      // Ensure user cannot update other users subcollection doc
      const db = getAuthedFirestore({ uid: uid }) // Authenticated, not superadmin
      const otherUserSubcolDoc = db
        .collection('users')
        .doc(otherUid)
        .collection('foo')
        .doc('bar')
      await firebase.assertFails(otherUserSubcolDoc.update({ foo: 'baz' }))
    })

    it('ensure cannot delete documents in subcollections belonging to another user', async () => {
      const adminDb = getAdminFirestore()
      const adminUserDoc = adminDb
        .collection('users')
        .doc(otherUid)
        .collection('foo')
        .doc('bar')
      await adminUserDoc.set({ foo: 'bar' })

      // Ensure user cannot delete subcollection for another user
      const db = getAuthedFirestore({ uid: uid }) // Authenticated, not superadmin
      const otherUserSubcolDoc = db
        .collection('users')
        .doc(otherUid)
        .collection('foo')
        .doc('bar')
      await firebase.assertFails(otherUserSubcolDoc.delete())
    })
  })
})
