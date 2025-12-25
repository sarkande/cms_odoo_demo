import { useTranslation } from '@/contexts/TranslationContext';
import styles from './UserListBlock.module.scss';

interface User {
  id: number;
  name: string;
  login: string;
  email: string;
  active: boolean;
}

interface UserListBlockProps {
  users: User[];
  limit?: number;
}

export default function UserListBlock({ users, limit }: UserListBlockProps) {
  const { t } = useTranslation();

  return (
    <div className={styles.userListBlock}>
      <h3>{t('block.team_members')}</h3>
      <div className={styles.userGrid}>
        {users.map((user) => (
          <div key={user.id} className={styles.userCard}>
            <h4>{user.name}</h4>
            <p className={styles.userInfo}>
              <strong>{t('user.login')}:</strong> {user.login}
            </p>
            {user.email && (
              <p className={styles.userInfo}>
                <strong>{t('user.email')}:</strong> {user.email}
              </p>
            )}
            <p className={`${styles.userStatus} ${user.active ? styles.active : styles.inactive}`}>
              {user.active ? `● ${t('user.active')}` : `○ ${t('user.inactive')}`}
            </p>
          </div>
        ))}
      </div>
    </div>
  );
}
