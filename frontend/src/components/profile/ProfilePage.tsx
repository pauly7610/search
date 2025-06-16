import React, { useEffect, useState } from 'react';
import styles from './ProfilePage.module.css';

interface UserProfile {
  id: string;
  name: string;
  email: string;
  avatar_url: string;
  bio: string;
}

export const ProfilePage: React.FC = () => {
  const [profile, setProfile] = useState<UserProfile | null>(null);
  const [edit, setEdit] = useState(false);
  const [form, setForm] = useState<UserProfile | null>(null);
  const [loading, setLoading] = useState(false);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);

  useEffect(() => {
    setLoading(true);
    setError(null);
    fetch('/api/v1/user/profile')
      .then(res => {
        if (!res.ok) throw new Error('Failed to fetch profile');
        return res.json();
      })
      .then(data => {
        setProfile(data);
        setForm(data);
      })
      .catch(err => setError(err.message || 'Unknown error'))
      .finally(() => setLoading(false));
  }, []);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
    if (!form) return;
    setForm({ ...form, [e.target.name]: e.target.value });
  };

  const handleSave = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!form) return;
    setSaving(true);
    setError(null);
    setSuccess(null);
    try {
      const res = await fetch('/api/v1/user/profile', {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(form),
      });
      if (!res.ok) throw new Error('Failed to save profile');
      const data = await res.json();
      setProfile(data);
      setForm(data);
      setEdit(false);
      setSuccess('Profile updated!');
    } catch (err: any) {
      setError(err.message || 'Unknown error');
    } finally {
      setSaving(false);
    }
  };

  if (loading) return <div className={styles.profilePage}><div className={styles.placeholder}>Loading...</div></div>;
  if (error) return <div className={styles.profilePage}><div className={styles.placeholder} style={{color: 'red'}}>{error}</div></div>;
  if (!profile) return null;

  return (
    <div className={styles.profilePage}>
      <header className={styles.header}>
        <h1>Profile</h1>
        {!edit && <button onClick={() => setEdit(true)} className={styles.editBtn}>Edit</button>}
      </header>
      <section className={styles.profileSection}>
        <div className={styles.avatarWrap}>
          <img src={profile.avatar_url} alt="avatar" className={styles.avatar} />
        </div>
        {edit && form ? (
          <form className={styles.form} onSubmit={handleSave}>
            <label>
              Name:
              <input name="name" value={form.name} onChange={handleChange} required />
            </label>
            <label>
              Email:
              <input name="email" value={form.email} onChange={handleChange} required type="email" />
            </label>
            <label>
              Avatar URL:
              <input name="avatar_url" value={form.avatar_url} onChange={handleChange} />
            </label>
            <label>
              Bio:
              <textarea name="bio" value={form.bio} onChange={handleChange} rows={3} />
            </label>
            <div className={styles.formActions}>
              <button type="submit" disabled={saving}>{saving ? 'Saving...' : 'Save'}</button>
              <button type="button" onClick={() => { setEdit(false); setForm(profile); }} disabled={saving}>Cancel</button>
            </div>
          </form>
        ) : (
          <div className={styles.profileInfo}>
            <div><strong>Name:</strong> {profile.name}</div>
            <div><strong>Email:</strong> {profile.email}</div>
            <div><strong>Bio:</strong> {profile.bio}</div>
          </div>
        )}
        {success && <div className={styles.success}>{success}</div>}
        {error && <div className={styles.error}>{error}</div>}
      </section>
    </div>
  );
}; 