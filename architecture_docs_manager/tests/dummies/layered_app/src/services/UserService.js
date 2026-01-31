
import { UserRepository } from '../repositories/UserRepository';

export class UserService {
    constructor() {
        this.repo = new UserRepository();
    }
}
