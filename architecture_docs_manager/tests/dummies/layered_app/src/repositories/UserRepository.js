
import { User } from '../models/User';

export class UserRepository {
    find() {
        return new User();
    }
}
